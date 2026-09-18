---
name: blender-previs
description: Build editable Blender white-box scenes from reference images, iterate camera moves, and export fast 720p previews. When requested, continue through FLORA MCP to photorealistic first/last frames and a Seedance 2.5 video using the previs motion. Use for reference-to-previs work, camera revisions, and the full previs-to-AI-video workflow.
---

# Blender previs

Turn the user's visual references and filmmaking direction into an editable scene and a readable motion-reference MP4. Optimize Blender work for iteration speed and spatial clarity. For a requested full workflow, continue through FLORA to a photorealistic AI video using the same motion. A render-only request ends with the Blender preview; creating or sharing the skill does not itself authorize uploads or paid generations.

## Runtime and portability

Distribute this entire `blender-previs` folder, including its `scripts`, `references`, and `agents` directories. A copied `SKILL.md` alone omits required helpers. The receiving environment needs Blender, Python 3, FFmpeg/FFprobe, and a connected FLORA MCP with access to the chosen models and billing workspace for the AI stage. Blender MCP is useful for the live scene but is not required for the background Python route. The skill does not install applications, transfer account access, or include generation credits.

Honor an existing workspace preference across runs; resolve its current ID from FLORA and never ask again merely because a new project is being created. Keep personal workspace IDs, project assets, credentials, and test photographs out of the distributable skill.

## Working defaults

- Blender MCP for inspecting and editing the open scene; background Blender for rendering. If MCP is unavailable but Blender is installed, standalone Python scene authoring is a valid fallback. Explain which route is being used.
- Neutral white-box geometry, true openings where the camera travels, simple materials, readable depth and silhouettes.
- **1280 × 720, 24 fps, Workbench**, studio lighting, material colors, shadows and cavity, eight AA samples, no motion blur. Use these from the first preview. Do not spend time on Cycles, textures, asset services, or GPU setup unless the task requires them.
- Eight seconds when the user wants a short move but leaves duration unspecified. Honor explicit duration, framing, aspect ratio, and render requirements; use 720 × 1280 for a vertical preview.
- **One working `.blend` file with named camera variations**, reusing scene geometry. A new camera ending does not require another full scene file. Retain the previous camera/action so the user can compare.
- Treat these as this user's defaults; more specific direction takes precedence. Do not require an approval round for every reversible modeling, framing, or rendering decision.

## 1. Read references and establish the shot

Inspect all supplied images. Distinguish architecture/subject references from screenshots specifying camera positions or framing. Preserve accessible original attachments in the project when useful, without recapturing or modifying them.

Extract only what the blockout needs: envelope, scale cues, openings, navigable volume, major structural elements, and visual landmarks. Briefly identify consequential assumptions, especially unseen geometry. Image interpretation does not establish measured dimensions or automatic image-to-3D accuracy.

Use the conversation to infer the start, route, end/reveal, timing, lens feel, and emotional pace. If a reference shows an exterior and a hollow interior, resolve how the camera enters. Ask only when missing direction would substantially change the result; continue independent geometry work while awaiting an optional answer. Do not invent a final shot when the user only asked for a building; deliver static 720p reviews and request camera direction afterward.

## 2. Check Blender and build or reuse the scene

Check the live scene and connection before proposing installations or resets. A missing server button does not mean a disconnected MCP: auto-start may already be enabled. Inspect the installed interface rather than relying on an old button label. Locate Blender, FFmpeg, and FFprobe from the actual environment.

Preserve unrelated existing scene content. Create or reuse clearly named project collections and a working scene. Author reusable Python with an explicit project root; do not hardcode a previous user's machine path. Make edits rerunnable by finding/updating named objects or replacing only generated objects owned by the task.

Use simple meshes/primitives for the recognizable structure. Build holes as real apertures for traversal, not dark planes. Keep the required interior volume clear. Floors, roofs, beams, and props should follow the new references; the refinery's open roof and absent floors are examples, not universal defaults.

Use fresh imports and explicit definitions in every MCP execution, or execute a saved script. Helpers from a prior code call may not remain in scope. Save the working scene, then inspect a small number of informative static views at 720p. Fix obstructed routes, missing openings, or unreadable geometry before animation.

## 3. Author cinematic camera motion

Translate the brief into a few timed beats: establish, approach, align, traverse, reveal, settle. Choose a fixed wide lens when it suits a drone-style move; 24 mm on a 36 mm sensor is a useful starting point, not a mandatory lens.

Use curved position and aim paths, controlled speed through openings, eased acceleration/deceleration, and restrained banking where requested. Separate travel from camera aim so interior parallax and reveals remain deliberate. Avoid sudden target flips, uncontrolled spline overshoot, exaggerated roll, and arbitrary FOV changes.

For implementation details, read [camera-motion.md](references/camera-motion.md) when authoring or revising animation. Bake or constrain motion as appropriate to the scene and Blender version. Set explicit frame range and fps; 192 frames at 24 fps produces eight seconds.

Check passage through scene geometry at subframes around narrow openings, including reasonable camera-body offsets. Report the sampled method and results accurately. Inspect camera frames before/at/after a crossing and at the reveal; centre clearance alone does not establish a good composition or eliminate near-plane clipping.

For “same move, different ending,” reuse the original evaluated world-space translation and alter only the requested orientation or timing. Keep an independently editable named camera/action. Compare translations frame by frame, and at subframes when the rig or interpolation could differ. If travel must change, explain the reason instead of silently changing it.

## 4. Render a few frames, then the complete 720p clip

Use [render_preview.py](scripts/render_preview.py) to execute the standard Workbench render and H.264 encode. Read [rendering.md](references/rendering.md) for invocation and failure handling. The helper takes explicit scene/camera names, honors the authored timeline and fps, and refuses to reuse an existing output directory.

Render a small storyboard of important beats first. Inspect it with image tools. A requested look-up should still show enough architecture to communicate the reveal: adjust tilt based on composition, not a memorized angle. Label draft images distinctly from final frames.

Once the storyboard is useful, render the full frame range without an extra approval checkpoint unless the user's workflow requires one. Keep each render revision in a distinct small output directory while retaining one working scene file. A render-only helper must not overwrite the `.blend`.

Validate expected frame count, dimensions, fps, duration, codec, and full MP4 decoding. If a check fails, fix the cause and rerender only what is needed. For a render stall, inspect the process/log before assuming a connection problem; report render progress concisely. Workbench does not require Cycles/Metal configuration.

## 5. Iterate and hand off

Deliver a clickable MP4, working `.blend`, and a few useful review frames with one sentence describing the motion and export specifications. On new notes, reuse the scene and unchanged path, modify the requested parameter, inspect the affected beats, and export the updated preview.

Keep a concise chronological Markdown production log beside the project: user's direction, reference paths, meaningful assumptions, camera variation, corrections, preview/final media links, and render/encode timings. Preserve existing detailed history rather than rewriting it. Do not make a new Notion page unless requested.

If usage records are available, sum distinct response usage once; cached inputs are a subset of input and reasoning outputs a subset of output. Separate active-turn wall time, render time, and between-turn time. Do not infer dollars from tokens or credit balance without applicable billing/rates. Use “not available” for unmeasured cost or usage; do not scan unrelated conversations to populate it.

Link PNGs in place rather than duplicating them. Full sequences can dwarf `.blend` files: retain them while reviewing and follow the user's retention choice before cleanup. Do not delete existing backups or change global backup settings automatically. Do not claim that rendered camera clips are desktop process recordings; capture a real walkthrough during future work only when requested and supported.

## 6. FLORA workflow — when the user requests the AI video stage

Read [flora-workflow.md](references/flora-workflow.md) and execute the sequence through the currently connected FLORA MCP:

1. Import the selected Blender render into the workflow's source video node.
2. Extract the actual first and last decoded frames, using the bundled [endpoint helper](scripts/extract_endpoints.py) when needed. Generate two photorealistic images using those compositions and the original references used to build the Blender scene.
3. Feed the Blender video and both generated images into **Seedance 2.5's mixed image/video mode**, set duration explicitly to the source video duration, ask the user for **resolution and bitrate mode** if not already specified, then generate within the authorized spend.

The skill stores the repeatable sequence; FLORA MCP resolves the current project, node IDs, model schemas, uploads, and execution dynamically. Read the named `workflow` group and its external input dependencies before editing. Reuse intended inputs through supported update tools; otherwise add a clearly named revision branch and identify it as such. Do not run unrelated nodes or duplicate an entire canvas diagram.

Show both styled endpoint images before the final video run so the user can redirect them. Combine that review with missing resolution/bitrate choices and a cost estimate. If the user has already authorized the exact settings and budget, inspect the frames and proceed without repeating the approval. General permission to use a skill is not a budget.

Current verified Seedance choices are **480p / 720p / 1080p** and **Standard / High** bitrate mode; refresh the live schema on each new workflow. The Blender 720p default is independent of final AI-video resolution. Do not invent a numeric bitrate setting or treat a zero-valued catalog cost estimate as free generation.

## Definition of done

For render-only work: the references are recognizably reflected in the scene; the directed route and reveal work; relevant clearance/composition checks pass; the MP4 matches the requested duration and default 720p preset and decodes fully; the editable working scene retains named variations; the user has direct links and a short production entry.

For a full workflow: the FLORA source and endpoint assets correspond to the selected render revision, the styled frames are reviewed, the actual Seedance 2.5 result is retrieved and checked against source timing and motion, the requested resolution/bitrate settings are recorded, and the project/output links and actual reported costs are delivered. Distinguish a prepared canvas from a completed generation and reference guidance from guaranteed exact camera or endpoint reproduction.
