# Character stand-ins

Previs only needs to show where a person is, how big they are, which way they face, and how they move through the shot. A jointed mannequin adds modeling time and failure modes (broken proportions, floating limbs, uncanny poses) without helping the camera move. The photorealistic person comes later from the AI step.

## Default: one primitive per character

Unless the user explicitly asks for a posed or limbed figure, build every character as a **single primitive**: a cylinder or a box. Do not build arms, legs, heads, or rigged armatures. Do not ask the user whether they want limbs; use the stand-in and mention it in one sentence.

| Character | Stand-in | Approx. size (metres) |
| --- | --- | --- |
| Adult, standing | Cylinder, radius 0.25 | 1.75 tall |
| Adult, walking or running | Same cylinder, animate location only | 1.75 tall |
| Child | Cylinder, radius 0.18 | 1.2 tall |
| Seated adult | Box, 0.5 x 0.5 | 1.2 tall |
| Crowd member | Cylinder, radius 0.22, shared material | 1.7 tall |

Prefer a cylinder for a single person. Use a box when the user asks for a box, or when a rectangular footprint reads better in a tight space. Match the scene's units and scale; if the scene is not in metres, convert.

## Make it readable

- Origin at the feet (base of the primitive) so location sits on the floor and the figure does not sink or float.
- One flat material per character, in a color that contrasts with the white-box (a mid grey-blue or warm grey). Use a different color per character when there is more than one, so the user can tell them apart in the preview.
- Name objects by role, for example `CHAR Woman`, `CHAR Guard 1`, and put them in a `Characters` collection so they can be hidden or replaced as a group.
- If facing direction matters to the shot, add a small flat wedge or a slightly different color on the front side. Do not add a face.
- Animate location (and rotation about Z for turns) only. Keep walking speed believable, about 1.3 m/s for a walk and 3 m/s for a jog, unless the brief wants something else.
- Check that the camera route and the character path do not intersect, and that the character is not hidden behind geometry at the key beats. Include characters in the storyboard frames.

## Rerunnable snippet

Adapt names, units, and sizes. Replace only objects this script owns.

```python
import bpy

def ensure_collection(name, scene):
    coll = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if coll.name not in scene.collection.children:
        scene.collection.children.link(coll)
    return coll

def make_stand_in(name, location, height=1.75, radius=0.25, shape="CYLINDER",
                  color=(0.45, 0.52, 0.62, 1.0), scene=None):
    scene = scene or bpy.context.scene
    coll = ensure_collection("Characters", scene)

    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    if shape == "BOX":
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        obj = bpy.context.active_object
        obj.scale = (radius * 2, radius * 2, height)
    else:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, vertices=32)
        obj = bpy.context.active_object

    obj.name = name
    # Move geometry so the origin sits at the feet.
    for v in obj.data.vertices:
        v.co.z += 0.5 * (1.0 if shape == "BOX" else height)
    obj.location = location  # z = floor height

    mat_name = f"{name} Mat"
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.diffuse_color = color
    obj.data.materials.clear()
    obj.data.materials.append(mat)

    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj
```

For a box, `scale` is applied to a unit cube, so apply the scale (`bpy.ops.object.transform_apply(scale=True)`) after the origin shift if later tools depend on real dimensions.

## When the user does ask for limbs

Only build a limbed figure when the user explicitly asks for one in this request (for example "give it arms and legs", "I need a posed mannequin"). Keep it low-poly, built from primitives (box torso, cylinder limbs, sphere head), and say plainly that it is a rough proportion guide. Do not treat an earlier request for limbs as permission to keep using them in new shots.

## What the AI step does with a stand-in

The Seedance and image-edit steps in [flora-workflow.md](flora-workflow.md) turn the stand-in into a real person. Describe the character in the endpoint-image prompts (age, build, clothing, hair), and tell the model to replace the stand-in with a person of the same height, position, and facing direction.
