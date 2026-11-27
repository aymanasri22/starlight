"""Headless Blender: light CGI with an HDRI and render it on a shadow catcher for compositing over a plate.

    blender -b --factory-startup --python studio/blender/integrate_cgi.py -- \
        --hdri X.hdr --out fg.png [--plate-out bg.png] [--yaw 0 --pitch -12 --fov 62] [--distance 4.5] \
        [--size 1280x720] [--samples 96] [--engine CYCLES|BLENDER_EEVEE] [--cam-height 1.6] [--blend out.blend]

Scene: the classic VFX lighting reference, an 18% grey ball and a chrome ball, standing on a shadow-
catcher ground plane. The camera sits at the HDRI's capture point, so the world background *is* a
perfectly matched plate (written with --plate-out). For a real photo plate, solve the camera first
(lens, height, horizon) and pass those values instead.

The foreground is written as straight-alpha RGBA where alpha carries the caught shadows, ready for
    out = fg.rgb * fg.a + plate * (1 - fg.a)
"""
import argparse
import math
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--hdri", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--plate-out")
ap.add_argument("--yaw", type=float, default=0.0)
ap.add_argument("--pitch", type=float, default=-12.0)
ap.add_argument("--fov", type=float, default=62.0)
ap.add_argument("--size", default="1280x720")
ap.add_argument("--samples", type=int, default=96)
ap.add_argument("--engine", default="CYCLES")
ap.add_argument("--cam-height", type=float, default=1.6)
ap.add_argument("--distance", type=float, default=4.5)
ap.add_argument("--strength", type=float, default=1.0)
ap.add_argument("--blend")
a = ap.parse_args(argv)

def assert_not_flat(path, min_std=0.01):
    """Fail loudly if a render is empty/flat (camera clipping, wrong aim, missing objects)."""
    img = bpy.data.images.load(path)
    px = list(img.pixels[:])
    n = len(px) // 4
    lum = [0.2126 * px[i * 4] + 0.7152 * px[i * 4 + 1] + 0.0722 * px[i * 4 + 2] for i in range(0, n, 97)]
    mean = sum(lum) / len(lum)
    std = (sum((v - mean) ** 2 for v in lum) / len(lum)) ** 0.5
    if std < min_std:
        raise SystemExit(f"STUDIO_FAIL render is flat (luma std {std:.4f}): check camera clip range, aim and objects")
    return std


scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

W, H = map(int, a.size.lower().split("x"))
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = W, H, 100
scene.view_settings.view_transform = "Standard"   # display-referred, matches the plate extraction
scene.view_settings.look = "None"

# --- world: equirect HDRI (Blender maps +X to the image centre) ---
world = bpy.data.worlds.new("hdri") if not scene.world else scene.world
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(a.hdri)
bg = nt.nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value = a.strength
out = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(env.outputs["Color"], bg.inputs["Color"])
nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

# --- camera at the capture point, looking along yaw (CCW from +X) / pitch ---
cam_data = bpy.data.cameras.new("cam")
cam_data.sensor_fit = "HORIZONTAL"
cam_data.angle = math.radians(a.fov)
cam_data.clip_start, cam_data.clip_end = 0.05, 5000.0
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
cam.location = (0, 0, a.cam_height)
cam.rotation_euler = (math.radians(90 + a.pitch), 0, math.radians(a.yaw - 90))
scene.camera = cam

# --- ground: shadow catcher ---
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.active_object
ground.is_shadow_catcher = True

# --- reference balls placed --distance m (default 4.5) in front of camera ---
yaw = math.radians(a.yaw)
fx, fy = math.cos(yaw), math.sin(yaw)
rx, ry = math.sin(yaw), -math.cos(yaw)


def ball(name, offset, radius, colour, metallic, roughness):
    d = a.distance
    loc = (fx * d + rx * offset, fy * d + ry * offset, radius)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=96, ring_count=48)
    o = bpy.context.active_object
    o.name = name
    bpy.ops.object.shade_smooth()
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*colour, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    o.data.materials.append(m)


ball("grey_18", -0.42, 0.22, (0.18, 0.18, 0.18), 0.0, 0.6)
ball("chrome", 0.42, 0.22, (0.95, 0.95, 0.95), 1.0, 0.02)

# --- render settings ---
scene.render.engine = a.engine
if a.engine == "CYCLES":
    scene.cycles.device = "CPU"
    scene.cycles.samples = a.samples
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "16"

if a.plate_out:  # background only: hide CG, render the world as the matched plate
    for o in scene.objects:
        if o.type == "MESH":
            o.hide_render = True
    scene.render.film_transparent = False
    if a.engine == "CYCLES":
        scene.cycles.samples = 4
    scene.render.filepath = a.plate_out
    bpy.ops.render.render(write_still=True)
    for o in scene.objects:
        o.hide_render = False
    if a.engine == "CYCLES":
        scene.cycles.samples = a.samples

scene.render.film_transparent = True
scene.render.filepath = a.out
bpy.ops.render.render(write_still=True)
if a.blend:
    bpy.ops.wm.save_as_mainfile(filepath=a.blend)
if a.plate_out:
    assert_not_flat(a.plate_out)
print(f"STUDIO_OK wrote {a.out}")
