"""Run inside background Blender; render Workbench previews without saving the scene."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

import bpy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', required=True)
    parser.add_argument('--camera', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--frames', help='Comma-separated storyboard frames; omit for full MP4')
    parser.add_argument('--width', type=int, default=1280)
    parser.add_argument('--height', type=int, default=720)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if min(args.width, args.height) < 2 or args.width % 2 or args.height % 2:
        raise ValueError('Dimensions must be positive even integers for H.264 yuv420p.')
    scene = bpy.data.scenes.get(args.scene)
    if scene is None:
        raise ValueError(f'Scene not found: {args.scene!r}')
    camera = scene.objects.get(args.camera)
    if camera is None or camera.type != 'CAMERA':
        raise ValueError(f'Camera not found in selected scene: {args.camera!r}')
    if scene.frame_start < 0 or scene.frame_end < scene.frame_start:
        raise ValueError('Use a nonnegative, ordered timeline before rendering.')
    fps = Fraction(str(scene.render.fps)) / Fraction(str(scene.render.fps_base))
    if fps <= 0:
        raise ValueError('Scene fps must be positive.')
    storyboard = args.frames is not None
    frames = (sorted(set(int(f.strip()) for f in args.frames.split(','))) if storyboard
              else list(range(scene.frame_start, scene.frame_end + 1)))
    if not frames or any(f < scene.frame_start or f > scene.frame_end for f in frames):
        raise ValueError('Selected frames must fall within the authored timeline.')
    ffmpeg = shutil.which('ffmpeg')
    ffprobe = shutil.which('ffprobe')
    if not storyboard and (not ffmpeg or not ffprobe):
        raise RuntimeError('Full export requires ffmpeg and ffprobe on PATH.')
    out = Path(args.output).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=False)
    frame_dir = out / 'frames'
    frame_dir.mkdir()
    scene.camera = camera
    # Render only the explicitly selected variation, independent of camera markers.
    for marker in scene.timeline_markers:
        marker.camera = None
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
    scene.render.use_border = False
    scene.render.use_crop_to_border = False
    scene.render.use_multiview = False
    scene.render.use_sequencer = False
    scene.render.use_compositing = False
    scene.render.film_transparent = False
    scene.render.use_motion_blur = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    scene.render.use_file_extension = True
    scene.render.use_overwrite = True  # Output directory was created exclusively above.
    scene.render.use_placeholder = False
    scene.frame_step = 1
    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.color_type = 'MATERIAL'
    shading.show_shadows = True
    shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.background_type = 'VIEWPORT'
    shading.background_color = (0.18, 0.18, 0.18)
    scene.display.render_aa = '8'
    report = {
        'source_blend': bpy.data.filepath,
        'blender_version': bpy.app.version_string,
        'scene': scene.name, 'camera': camera.name,
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'mode': 'storyboard' if storyboard else 'full',
        'engine': scene.render.engine, 'resolution': [args.width, args.height],
        'fps': str(fps), 'frames': frames, 'frame_count': len(frames),
        'authored_clip_duration_seconds': float(Fraction(scene.frame_end - scene.frame_start + 1) / fps),
        'status': 'rendering',
    }
    report_path = out / 'render_report.json'

    def save_report():
        report_path.write_text(json.dumps(report, indent=2) + '\n')

    save_report()
    try:
        start = time.perf_counter()
        if storyboard:
            for frame in frames:
                scene.frame_set(frame)
                scene.render.filepath = str(frame_dir / f'frame_{frame:04d}.png')
                bpy.ops.render.render(write_still=True, scene=scene.name)
        else:
            scene.render.filepath = str(frame_dir / 'frame_')
            bpy.ops.render.render(animation=True, scene=scene.name)
        report['render_seconds'] = time.perf_counter() - start
        expected = {f'frame_{f:04d}.png' for f in frames}
        actual = {p.name for p in frame_dir.glob('*.png') if p.stat().st_size > 0}
        if expected != actual:
            raise RuntimeError(f'Frame mismatch: missing {sorted(expected - actual)}, extra {sorted(actual - expected)}')
        if not storyboard:
            video = out / 'preview.mp4'
            start = time.perf_counter()
            subprocess.run([
                ffmpeg, '-hide_banner', '-loglevel', 'error', '-n',
                '-framerate', str(fps), '-start_number', str(frames[0]),
                '-i', str(frame_dir / 'frame_%04d.png'), '-frames:v', str(len(frames)),
                '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(video),
            ], check=True)
            report['encode_seconds'] = time.perf_counter() - start
            start = time.perf_counter()
            probe = json.loads(subprocess.run([
                ffprobe, '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames,duration:format=size,duration',
                '-of', 'json', str(video),
            ], check=True, text=True, capture_output=True).stdout)
            stream = probe['streams'][0]
            duration = float(Fraction(len(frames)) / fps)
            checks = [stream['codec_name'] == 'h264', stream['pix_fmt'] == 'yuv420p',
                      stream['width'] == args.width, stream['height'] == args.height,
                      int(stream['nb_frames']) == len(frames),
                      Fraction(stream['r_frame_rate']) == fps,
                      abs(float(stream['duration']) - duration) < 0.001]
            if not all(checks):
                raise RuntimeError(f'Encoded video does not match authored export: {probe}')
            subprocess.run([ffmpeg, '-v', 'error', '-xerror', '-i', str(video), '-f', 'null', '-'], check=True)
            report.update(video=str(video), probe=probe, full_decode_passed=True,
                          validation_seconds=time.perf_counter() - start)
        report['status'] = 'complete'
    except Exception as exc:
        report.update(status='failed', error=str(exc))
        raise
    finally:
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        save_report()
    print('PREVIS_REPORT ' + str(report_path), flush=True)


if __name__ == '__main__':
    main()
