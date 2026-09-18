"""Extract exact decoded MP4 endpoints with FFmpeg; no additional Python packages.

Usage: python3 extract_endpoints.py preview.mp4 --output endpoints-v01
The output directory must not exist. No remote calls or generation charges.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.video.resolve(strict=True)
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
        '-show_streams', '-show_format', '-of', 'json', str(source)
    ]))
    stream = probe['streams'][0]
    count = int(stream['nb_read_frames'])
    if count < 2:
        raise ValueError('Two distinct endpoints require at least two decoded frames.')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-xerror', '-i', str(source),
               '-map', '0:v:0', '-vf', f'select=eq(n\\,0)+eq(n\\,{count-1})',
               '-fps_mode', 'vfr', '-frames:v', '2', str(output / 'endpoint-%02d.png')]
    started = time.perf_counter()
    subprocess.run(command, check=True)
    images = sorted(output.glob('endpoint-*.png'))
    if len(images) != 2:
        raise RuntimeError(f'Expected two endpoint PNGs, found {len(images)}')
    for image, name in zip(images, ('first.png', 'last.png')):
        image.rename(output / name)
    manifest = {
        'source_path': str(source), 'source_sha256': sha256(source),
        'decoded_frame_count': count, 'selected_frame_indices': [0, count-1],
        'duration_seconds': float(stream.get('duration', probe['format']['duration'])),
        'width': stream['width'], 'height': stream['height'],
        'average_frame_rate': stream['avg_frame_rate'],
        'extraction_seconds': time.perf_counter()-started,
        'ffmpeg_argv': command,
        'endpoints': {name: sha256(output / name) for name in ('first.png', 'last.png')},
        'ffprobe': probe,
    }
    (output / 'endpoints.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({key: manifest[key] for key in (
        'decoded_frame_count', 'selected_frame_indices', 'duration_seconds',
        'width', 'height', 'extraction_seconds')}))


if __name__ == '__main__':
    main()
