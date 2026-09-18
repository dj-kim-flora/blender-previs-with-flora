# Fast render and export

The bundled helper runs **inside Blender**, using its `bpy` module. FFmpeg and FFprobe must be available on `PATH` for a full clip; storyboard mode does not need them. No extra Python packages are required. The helper was exercised with Blender 4.5.4; inspect incompatibilities on other versions rather than assuming they share every property.

Set the desired timeline, fps, camera, and Workbench defaults in the editable scene while authoring it, then save the one working `.blend`. The helper overrides render appearance in a background process but never saves the scene. It preserves that scene's timeline and fps, turns off camera marker overrides for its background render, and uses the explicitly selected camera throughout.

Replace example paths and camera/scene names with values actually inspected. Locate the Blender executable; on this user's Mac the existing installation is `/Applications/Blender.app/Contents/MacOS/Blender`. Use an absolute helper path resolved from this skill directory. Do not make the skill depend on the original refinery workspace.

Example storyboard invocation (choose frames that exist in the actual timeline):

```bash
"/Applications/Blender.app/Contents/MacOS/Blender" --background scenes/previs.blend --python-exit-code 1 --python /absolute/path/to/blender-previs/scripts/render_preview.py -- --scene "PREVIS" --camera "CAM 01" --output renders/shot01/storyboard_r01 --frames 1,111,192
```

Full export, including encode and verification:

```bash
"/Applications/Blender.app/Contents/MacOS/Blender" --background scenes/previs.blend --python-exit-code 1 --python /absolute/path/to/blender-previs/scripts/render_preview.py -- --scene "PREVIS" --camera "CAM 01" --output renders/shot01/clip_r01
```

`--width 720 --height 1280` supports a vertical shot. Frame rate comes from the authored scene, including `fps_base`. Full mode renders every frame in the inclusive timeline, ignoring a saved preview frame-step value. It produces:

- `frames/frame_0001.png` etc., numbered with the authored frame numbers.
- `preview.mp4`: H.264, CRF 18, `yuv420p`, fast-start metadata, no audio.
- `render_report.json`: source/camera, resolution, frames/fps, measured render/encode/check times, FFprobe metadata, and full-decode result.

Storyboard mode writes selected frames and a report, without a video. Full mode expects one animated camera; split cuts into individual clips or use a separately authored sequence renderer when a user specifically requests cuts.

An existing output directory is refused to prevent stale or overwritten frames. Pick a new revision directory for another run. A failed run can leave partial evidence there; inspect the failure and use a new directory for the corrected attempt. Original frames and scene files are never automatically deleted.

Use the execution tool's required sandbox escalation if background Blender is blocked. Keep stdout in a per-run log when helpful, with that log **outside** the new output directory so the helper can create it exclusively. Check the process exit code and the report: Blender's `--python-exit-code 1` ensures Python failures are visible to the caller. Do not loop on missing MCP buttons or switch to an expensive renderer to solve an execution-permission error.

Render wall time in the report measures Blender's render calls; it excludes background-process startup. Encoding and validation are separately timed. These values overlap the agent turn and must not be added to that turn duration as extra elapsed work. The report does not infer token usage, energy use, or billing.
