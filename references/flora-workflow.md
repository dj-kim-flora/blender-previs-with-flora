# FLORA workflow: previs to photorealistic video

Use this phase when the user asks to continue a Blender preview into FLORA, requests the full workflow, or asks to execute the named `workflow` group. Keep the orchestration in the skill and controls on the live canvas. Do not lock the portable skill to a personal project ID, workspace, asset URL, or node UUID.

## Run contract and user controls

Before execution, resolve the chosen previs MP4, original architecture/subject references, intended FLORA project and billing workspace, visual treatment, final resolution, bitrate mode, and authorized generation spend. Infer existing choices from the current conversation. Ask for missing resolution and bitrate before generating the final video, with current schema-valid options; do not assume that the 720p Blender setting decides final output quality.

Two modes share the same workflow:

- **Guided full run:** import, extract, generate endpoint images, review them, collect final output choices/cost authorization if missing, then generate the video.
- **Prepare and hand off:** build or update the inputs/connections/settings and leave the final generation under the user's control in FLORA. Do not describe idle nodes as completed outputs.

Users can revise lighting, prompts, image model, selected endpoint results, resolution, and bitrate dynamically. Keep the sequence and input roles stable. A request to modify this skill or assess feasibility is not a request to spend credits testing it.

## Inspect the existing group

Use `flora_get_project` to confirm the project's workspace, `flora_get_canvas` for structure/groups, and `flora_list_canvas_nodes` for media asset URLs/UUIDs. A `workflow` group is a canvas container, not necessarily a saved executable FLORA Technique. Do not call `flora_run_technique` on a group label.

Read incoming edges crossing the group boundary: a reference outside the group can still drive one of its image nodes. The source example's `Frame 1` feeds `Night Time`, `Frame-2` feeds `Architecture Visualization`, and both styled images plus the previs video feed the final video node. One reference feeding `Night Time` sits outside the group. Preserve that dependency or explicitly rebind it to the new user's corresponding source reference. Night treatment is not mandatory for unrelated scenes.

The inspected source group had standalone extracted frame images, not a visible automatic video-to-extraction chain. Refresh both endpoint assets for every newly selected render. Never assume a renamed source node updates downstream frame images.

Graph reads do not expose every saved prompt or parameter. Do not claim to have recovered settings absent from the tool response. Use available detailed node tools or the FLORA UI for those fields. If no supported update path exists, preserve the original group and create a clearly identified revision branch with equivalent dependencies, or hand off the unsupported edit. Do not assume an asset-attach call replaces the first node: it may create a new node.

## 1. Import the rendered video

Probe the selected MP4 locally with FFprobe: decoded frame count, fps, duration, width/height, and aspect ratio. Record the source path, hash, and render revision so later inputs cannot silently refer to another shot.

If the exact asset already exists in the target canvas, reuse it. Otherwise use `flora_create_asset` with `source="signed-url"`, upload the local bytes to the returned multipart URL with every supplied form field and the file field last, and call `flora_complete_asset`. Follow the actual returned schema. Never put local filesystem paths into a remote URL field, base64 large files through `execute`, or reserve an upload without completing it.

Bind the completed video to the intended source node using supported APIs/UI. If a new revision branch is needed, use `flora_attach_asset` or a Video input node with its hosted content URL, and wire that branch explicitly. Import or reuse the original architectural reference images in the same project. These reference photographs guide appearance; the Blender frames guide composition.

## 2. Extract and restyle first/last frames

Discover the current `extract-video-frames` action with `flora_search_actions`. At validation time it supports `mode="single"` with `time_percent=0` or `100`, or evenly spaced extraction with a frame count. Prefer two explicit endpoint extractions; verify that 100% resolves to the last decoded frame rather than an out-of-range seek, black frame, or approximate earlier frame. Use the actual action input-wiring schema; merely adding an action node does not prove its source video is connected.

When canvas actions cannot reliably expose the endpoints, use [extract_endpoints.py](../scripts/extract_endpoints.py): `python3 /path/to/skill/scripts/extract_endpoints.py preview.mp4 --output endpoints-v01`. It counts decoded frames, extracts indices 0 and N−1, and records source/endpoint SHA-256 hashes and metadata. The output directory must be new. Upload both results and retain this manifest with the project. Do not substitute an arbitrary midpoint or seek to timestamp equal to clip duration. For 192 frames at 24 fps, the final displayed frame begins at 7.9583 seconds while the video duration is 8.000 seconds.

Create two image-edit branches:

- **First composition + relevant original references → photorealistic first frame.**
- **Last composition + relevant original references → photorealistic last frame.**

Use a current multi-reference image-edit model. **Nano Banana Pro**, verified as `i2i-gemini-3-pro`, is a starting choice when an image model has not been specified; preserve an existing explicitly chosen compatible model. Its live availability was verified, but the existing canvas read did not expose the saved image-node model settings. Refresh `flora_list_models` for the current ID, aspect ratios, resolution, price, and input support. Do not silently route to a text-only model. When running the prepared canvas with multiple images, FLORA may resolve `i2i-gemini-3-pro` to `is2i-gemini-3-pro`; record the actual returned variant rather than treating this as a model mismatch.

For new image generations whose inputs already live on the canvas, `flora_generate.reference_node_ids` wires their image outputs into an image-edit model. This field is **image-generation-only**; it is not the way to pass references to the final video model. Preserve the frame-to-result mapping and actual reference image inputs rather than relying on text alone.

Prompt each edit with explicit roles, adapting nouns to the new scene:

> Replace the white-box materials in the Blender frame with photorealistic surfaces, architectural details, and lighting informed by the supplied reference photographs. Preserve the Blender frame's camera position, lens perspective, framing, building silhouette, openings, and major structural layout. Use the same material palette, time of day, light direction, and grade as the companion endpoint. Keep the traversed opening and open interior consistent with the previs; add no obstruction or geometry that changes the camera route.

Original photos may contain elements deliberately omitted from the scene, such as a glazed rooftop. Reference appearance must not reintroduce those elements without direction. If both endpoint generations can run independently, generate them concurrently within the authorized spend; if the last endpoint needs the accepted first result for consistency, run sequentially with that extra reference.

Inspect actual image outputs using available image-capable tools, not URLs/metadata alone. Compare perspective, window placement, space, lighting, and material identity. Show both endpoint results with their source compositions. Fix a demonstrated issue within the authorized retry budget; avoid endless rerolls.

## 3. Configure and generate Seedance 2.5

Discover **Seedance 2.5 with `mixed-to-video` capability**. The live registry verified on September 8, 2026 exposes **`isv2v-seedance-2-5`**. Do not substitute `r2v-seedance-2-5` merely because it says “reference”: its advertised capability was `frames-to-video`. A text-only or image-only variant cannot replace the Blender motion reference.

Wire **three actual media inputs** into the video node: the original previs video, the photorealistic first frame, and the photorealistic last frame. Use the supported canvas edge/input-role schema and clear prompt references. Two incoming images are appearance/endpoint guidance; do not claim the mixed mode guarantees exact first/last-frame enforcement or mathematically identical travel.

When constructing a new branch, `flora_add_to_canvas` supports Video nodes and per-node `model`, `prompt`, and `model_parameters`. Use an explicit `(Video)` suffix and the discovered mixed model. Existing nodes appear as bare IDs in edges, never redeclare them with labels. Do not submit the entire diagram from `flora_get_canvas` back to the add operation: that duplicates existing nodes. **Refresh `flora_get_canvas` immediately before each run. Short `n#` identifiers can change after a node completes or the UI updates it; an ID from the add response is not durable. Prefer stable node IDs from `flora_list_canvas_nodes` when available, and identify an unrendered node by its current type and incoming dependencies. Confirm that the run response resolves the intended model before continuing.** The temporary labels used in the request are not execution IDs. Uploaded node IDs can be `mcp_upload_...` strings rather than UUIDs; use the returned IDs verbatim. A Mermaid `subgraph` does not create a FLORA group: the current add tool warns that it ignores subgraphs and creates ungrouped nodes. Create a requested visual group through supported UI/tools, or clearly report the ungrouped branch; do not repeatedly submit it.

If a canvas/UI exposes dedicated reference tags or input roles, assign them and refer to those exact bindings in the prompt. Otherwise clearly identify the visual content and confirm supported input delivery before running. Do not invent unsupported `first_frame`, `last_frame`, `video_url`, or `reference_node_ids` parameters for a video generation call.

Prompt intent:

> Use the Blender previs video as the camera-motion and timing reference: preserve its approach, traversal, arcs, and final reveal as closely as possible. Use the photorealistic first-frame image for the opening composition and appearance and the photorealistic last-frame image for the ending composition and appearance. Maintain one coherent scene, consistent materials and lighting, and a continuous shot with no cuts, extra camera moves, or route-blocking geometry.

Current verified `model_parameters` are:

```json
{
  "duration": "8",
  "aspect_ratio": "16:9",
  "resolution": "720p",
  "bitrate_mode": "standard"
}
```

This is an example for an eight-second landscape source, not a set of silently chosen output settings. At verification, duration offers whole seconds **4 through 30** plus `auto`, resolution offers **480p / 720p / 1080p**, and bitrate mode offers **standard / high**. Refresh these options during execution. Bitrate mode is a provider preset, not a numeric Mbps field.

Set duration explicitly to the probed source duration when supported. For a non-integer duration or duration outside the supported range, explain the mismatch and ask whether to trim, retime, split, or keep manual control; do not silently round or use `auto` while promising equal length. Set aspect ratio to match the source where supported.

Ask together, unless already answered: **“What final resolution (480p, 720p, or 1080p) and bitrate mode (Standard or High) should Seedance use?”** Show a current cost estimate for the intended two image generations and final video. The Seedance catalog returned `estimated_credits: 0` during inspection; that is insufficient evidence of free generation. Use a real quote/UI estimate if available or disclose that cost is unavailable and obtain a spending limit before paid execution. Honor existing explicit budget authorization without repeating it. On insufficient credits, stop and report the provider's upgrade/error guidance rather than retrying.

Generate only the intended final node after its inputs complete and settings are resolved, using `flora_run_canvas_nodes` or the supported equivalent. Record the returned run/generation ID and poll that existing run; never resubmit just because a request timed out. If the mixed model fails immediately with a generic error despite completed inputs and valid settings, inspect the native FLORA node for detailed diagnostics. One native UI execution with those same intended inputs is a reasonable fallback after the API run is confirmed failed; identify it in the handoff as a UI fallback, not an MCP-only success. Avoid unchanged API retry loops. Do not execute the entire original canvas, timelines, comparison videos, or unrelated branches.

## Verify, log, and rerun narrowly

Retrieve the completed video and inspect representative beginning, traversal, and ending frames against the previs. Probe actual output duration, dimensions, fps, and full decoding. Preserve provider output and report any drift or mismatch. If a separate exact-rate transcode is requested, distinguish that export operation from Seedance's bitrate preset and preserve the original.

Log project/workspace, source video hash and duration, endpoint assets, original references, prompts, model IDs, selected settings, run IDs, measured wall times, provider-reported costs, output URLs, and limitations. Keep `estimated_credits` separate from `charged_cost`: they are different fields and may use different units. The official FLORA SDK documents `charged_cost` in USD. Record provider values verbatim and preserve catalog credits separately; do not sum a credit estimate and a dollar cost. A workspace's billing identity stays project-specific; never select the first accessible workspace merely because it is listed first.

Rerun only invalidated stages: a new camera render invalidates both extracted/styled endpoints and the final video; a material/reference change invalidates the styled endpoints and video; a resolution/bitrate-only change normally needs only the final video. Re-read the canvas before changing it because the user may have edited inputs manually.

## Evidence boundary

September 11, 2026 test: two real architectural photographs drove a newly authored Blender walking scene; the bundled renderer produced a validated eight-second 720p MP4; exact decoded endpoints and both photographs were uploaded through MCP; both Nano Banana Pro endpoint images completed and were visually inspected. The correct mixed Seedance 2.5 canvas run, with both images and the original video attached at 8 seconds / 1080p / High, failed immediately with `GENERATION_GENERIC_ERROR`. The native UI showed the intended three media inputs and a $9.775 quote; a completed final video has not yet been verified. Treat this as a usable tested previs/image workflow with an unresolved final-video execution dependency, not an MCP-only end-to-end pass.

The test also exposed unstable short node IDs, ignored Mermaid groups, and a zero catalog video-price estimate. The instructions above capture those observed limitations. Public canvas tools expose graph structure and output URLs but not every saved setting; detailed diagnostics, grouping or native generation may require supported UI access.
