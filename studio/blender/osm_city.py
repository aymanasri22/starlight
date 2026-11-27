"""Headless Blender: extrude OpenStreetMap building footprints into a 3D city (for map flights / title cards).

    blender -b --factory-startup --python studio/blender/osm_city.py -- \
        --osm lujiazui.json --out city.png [--size 1600x900] [--samples 32] [--blend city.blend] \
        [--default-height 18] [--cam-dist 3400] [--cam-elev 30] [--cam-az 215]

Footprints come from `studio/lib/assets.py osm-buildings` (ODbL: credit "(c) OpenStreetMap contributors").
Lat/lon are projected to local metres (equirectangular about the bbox centre: accurate to well under 1%
over a few km). Buildings without height tags get --default-height. Named landmarks are kept as object
names so they can be animated or highlighted. The look here is a neutral clay study; the Motion Designer
and Cinematographer design the real one.
"""
import argparse
import json
import math
import sys

import bmesh
import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--osm", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--size", default="1600x900")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--default-height", type=float, default=18.0)
ap.add_argument("--cam-dist", type=float, default=3400.0)
ap.add_argument("--cam-elev", type=float, default=30.0)
ap.add_argument("--cam-az", type=float, default=215.0)
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


data = json.load(open(a.osm))
blds = [b for b in data["buildings"] if len(b["coords"]) >= 4]
lat0 = sum(c[0] for b in blds for c in b["coords"]) / sum(len(b["coords"]) for b in blds)
lon0 = sum(c[1] for b in blds for c in b["coords"]) / sum(len(b["coords"]) for b in blds)
R = 6371008.8
kx, ky = math.radians(1) * R * math.cos(math.radians(lat0)), math.radians(1) * R


def xy(lat, lon):
    return ((lon - lon0) * kx, (lat - lat0) * ky)


scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

clay = bpy.data.materials.new("clay")
clay.use_nodes = True
clay.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.62, 0.6, 0.57, 1)
clay.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
hero = bpy.data.materials.new("landmark")
hero.use_nodes = True
hero.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.78, 0.55, 0.3, 1)

made = 0
for b in blds:
    pts = [xy(*c) for c in b["coords"]]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        continue
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2
    if abs(area) < 4:
        continue
    if area < 0:
        pts.reverse()
    h = b["height"] or a.default_height
    me = bpy.data.meshes.new(f"b{b['id']}")
    bm = bmesh.new()
    verts = [bm.verts.new((x, y, 0)) for x, y in pts]
    try:
        face = bm.faces.new(verts)
    except ValueError:
        bm.free()
        continue
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, vec=(0, 0, h), verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(b["name"] or f"bldg_{b['id']}", me)
    ob.data.materials.append(hero if (b["height"] or 0) > 300 else clay)
    scene.collection.objects.link(ob)
    made += 1

bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, -0.05))
ground = bpy.context.active_object
gm = bpy.data.materials.new("ground")
gm.use_nodes = True
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.16, 0.17, 0.19, 1)
ground.data.materials.append(gm)

# sky + sun
world = bpy.data.worlds.new("sky")
scene.world = world
world.use_nodes = True
bgn = world.node_tree.nodes["Background"]
bgn.inputs["Color"].default_value = (0.55, 0.62, 0.75, 1)
bgn.inputs["Strength"].default_value = 0.6
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.5
sun.data.angle = math.radians(2)
sun.rotation_euler = (math.radians(50), 0, math.radians(140))
scene.collection.objects.link(sun)

# orbiting-style camera aimed at the centre of the tallest buildings
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens = 40
cam.data.clip_start = 1.0
cam.data.clip_end = 50000.0  # default clip_end (100 m) hides a city seen from 1.7 km
scene.collection.objects.link(cam)
az, el = math.radians(a.cam_az), math.radians(a.cam_elev)
cam.location = (a.cam_dist * math.cos(el) * math.cos(az), a.cam_dist * math.cos(el) * math.sin(az), a.cam_dist * math.sin(el))
target = bpy.data.objects.new("target", None)
target.location = (0, 0, 180)
scene.collection.objects.link(target)
con = cam.constraints.new("TRACK_TO")
con.target = target
con.track_axis = "TRACK_NEGATIVE_Z"
con.up_axis = "UP_Y"
scene.camera = cam

W, H = map(int, a.size.lower().split("x"))
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = a.samples
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
scene.render.filepath = a.out
bpy.ops.render.render(write_still=True)
if a.blend:
    bpy.ops.wm.save_as_mainfile(filepath=a.blend)
std = assert_not_flat(a.out)
print(f"STUDIO_OK {made} buildings -> {a.out} (luma std {std:.3f})")
