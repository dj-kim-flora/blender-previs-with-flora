# Camera authoring notes

Use the current scene's scale, constraints, and Blender API. These are techniques validated by the refinery workflow, not fixed refinery geometry or a shot template to impose on every brief.

## Curves and orientation

A clamped cubic spline for both position and aim can supply continuous acceleration with explicit endpoint velocities. For a narrow aperture, constrain alignment on either side and sample between waypoints to catch overshoot. More sophisticated motion is only useful if the framing stays readable.

The refinery example used a fixed 24 mm lens, an eight-second curved exterior approach, a window crossing near 4.6 seconds, and a banked interior reveal. Roll of roughly two to three degrees gave motion cues without excessive tilt. Re-author route, crossing time, and roll for each new brief.

For a camera with Blender's local forward axis `-Z` and up axis `Y`:

```python
q = (target - location).to_track_quat('-Z', 'Y')
q = q @ Quaternion((0, 0, 1), bank_radians)
if previous is not None and q.dot(previous) < 0:
    q.negate()
```

Keep quaternion signs continuous. For rotation differences, use the shortest arc:

```python
angle = 2 * math.acos(min(1.0, abs(q0.normalized().dot(q1.normalized()))))
```

If baking one key per frame, linear interpolation avoids additional Bezier overshoot between dense keys. It approximates the authored curve; evaluate subframes if exact continuity or constraints matter. Blender action APIs vary: inspect the installed version's action/layer/channelbag interface before editing key interpolation.

## Same travel, altered gaze

Capture the source camera's evaluated world transform at each frame before editing. Copy camera data and use an independent animation action. For a source with parenting, drivers, or constraints, either preserve the equivalent rig or bake evaluated world transforms onto an unparented, unconstrained camera. Merely copying `location` and `rotation_quaternion` can lose the original world-space motion.

A quintic smoothstep makes an orientation change arrive gently:

```python
u = max(0.0, min(1.0, (t - tilt_start) / (last_pose_time - tilt_start)))
ease = u**3 * (10 - 15*u + 6*u*u)
```

Require `tilt_start < last_pose_time`. Slerp toward an authored final orientation, or apply a suitable local pitch delta. With roll or complex yaw, a local-X rotation does not guarantee an exact world-space pitch: measure the resulting forward vector and inspect composition.

In the refinery case, tilt began at 4.9 seconds. A +47.2° first draft showed too much sky; +32.5° retained walls, beams, and the chimney. This is a lesson to inspect the view, not a default final angle.

For unchanged-travel requests, compare evaluated world translations across the frame range. Record maximum deviation and tolerance; the refinery test measured 0.0 m at all 192 frames. Use separate named cameras/actions in the same file rather than copying the building into another file.

## Clearance and timing

Sample ray segments along the evaluated path at approximately four times the playback fps, increasing density around tight turns/openings when needed. A centre path plus six axis offsets representing a modest body radius is a useful quick check. Choose the radius for scene scale; the refinery used 0.20 m. These samples are not an exhaustive swept-volume collision proof.

Check wall thickness, window jambs, lintels, beam spans, ground, and ceiling near the route. Inspect frames around crossings for near-plane clipping even if sampled rays pass. Pose positions, camera aim, and the finite near plane all influence whether traversal looks convincing.

At integer fps, author `N = round(duration * fps)` frames, usually starting at 1. The last pose time relative to the first is `(N - 1) / fps`; the encoded clip duration is `N / fps`. Preserve explicit fps and frame range during rendering instead of silently retiming an existing animation.
