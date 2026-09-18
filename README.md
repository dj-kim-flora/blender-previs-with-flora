# Blender Previs + FLORA

An agent skill (`blender-previs`) that turns reference images and camera direction into an editable Blender white-box scene and a fast 720p motion-reference MP4. On request, it continues through FLORA MCP to photorealistic first/last frames and a Seedance 2.5 video that follows the previs motion.

## What it does

1. **Previs** — builds a neutral white-box scene from reference images, authors a curved camera move, and renders a 1280×720, 24 fps Workbench preview (H.264). A single `.blend` holds named camera variations for comparison.
2. **AI video (optional)** — imports the preview into FLORA, extracts the exact first/last frames, generates photorealistic endpoint images, then runs Seedance 2.5 in mixed image/video mode. Spend is only incurred when you authorize it.

A render-only request stops at the Blender preview.

## Layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Skill definition and full workflow instructions |
| `agents/openai.yaml` | Display name and default prompt for the agent UI |
| `references/camera-motion.md` | Camera path, aim, and clearance techniques |
| `references/rendering.md` | Render helper invocation and failure handling |
| `references/flora-workflow.md` | Previs-to-video steps on the FLORA canvas |
| `scripts/render_preview.py` | Runs inside background Blender: storyboard frames or full MP4 |
| `scripts/extract_endpoints.py` | Extracts exact first/last decoded frames via FFmpeg |

## Requirements

- Blender (helper tested with 4.5.4)
- Python 3
- FFmpeg and FFprobe on `PATH`
- Connected FLORA MCP with access to the chosen models and billing workspace (AI stage only)
- Blender MCP is optional; standalone Python scene authoring works as a fallback

## Usage

Install or distribute the whole folder — `SKILL.md` alone omits the required helpers. Then ask, for example:

> Use $blender-previs to turn my reference images and camera direction into an editable scene and quick 720p preview, then continue through FLORA when I request the final AI video.

Helper scripts (paths and names are examples):

```bash
# Storyboard frames
Blender --background scenes/previs.blend --python-exit-code 1 \
  --python scripts/render_preview.py -- \
  --scene "PREVIS" --camera "CAM 01" --output renders/shot01/storyboard_r01 --frames 1,111,192

# First/last frames of a rendered preview
python3 scripts/extract_endpoints.py preview.mp4 --output endpoints-v01
```

Both helpers refuse to reuse an existing output directory. See `references/rendering.md` for the full-export invocation.

## Notes

- The skill does not install software, transfer account access, or include generation credits.
- Keep personal workspace IDs, project assets, and credentials out of the distributed folder.
