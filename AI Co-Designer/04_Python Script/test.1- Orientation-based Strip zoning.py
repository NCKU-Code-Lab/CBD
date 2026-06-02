import json
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import explain_validity

# === 1. 定義 outline/courtyard/core/usable ===
outline = Polygon([
    (397.676, -81.54), (389.119, -81.54),
    (389.119, -151.46), (434.669, -151.46),
    (434.669, -140.643), (431.530, -140.643),
    (431.530, -90.221), (435.712, -90.221),
    (435.712, -83.048), (397.676, -83.048),
    (397.676, -81.54)
])
courtyard = Polygon([
    (403.669, -136.739), (416.980, -136.739),
    (416.980, -91.865), (403.669, -91.865),
    (403.669, -136.739)
])
core = Polygon([
    (423.140, -140.239), (416.980, -140.239),
    (416.980, -151.462), (434.669, -151.462),
    (434.669, -140.643), (431.530, -140.643),
    (431.530, -140.239), (423.140, -140.239)
])
usable = outline.difference(unary_union([courtyard, core]))

# === 2. 條帶與空間設定 ===
spaces = [
    # 南條帶（左到右）
    ("A", 230.0, [113, 168, 240], "Art & DIY room", "south"),
    ("B", 243.0, [113, 168, 240], "Social Lounge", "south"),

    # 西條帶（下到上）
    ("C", 90.0, [97, 97, 97], "Kitchen", "west"),
    ("D", 220.0, [211, 34, 240], "Restaurant", "west"),
    ("E", 120.0, [36, 60, 240], "Lobby", "west"),
    ("F", 150.0, [211, 34, 240], "Café", "west"),

    # 北條帶（左到右）
    ("G", 250.0, [97, 97, 97], "Office", "north"),
    ("H", 25.0, [113, 168, 240], "Meeting & Archive Room", "north"),

    # 東條帶（下到上）
    ("I", 50.0, [97, 97, 97], "Public Toilet", "east"),
    ("J", 170.0, [113, 168, 240], "Library", "east"),
    ("K", 100.0, [113, 168, 240], "Herb Tea Bar", "east"),
    ("L", 180.0, [113, 168, 240], "Dining Room", "east"),
    ("M", 180.0, [113, 168, 240], "Cooking Class", "east"),
    ("N", 75.0, [113, 168, 240], "Multi-use Hall", "east"),
]





# === 3. 條帶 bounding box（根據 usable 自行微調區域）===
zones_config = {
    "south": {"minx": 403.669, "maxx": 431.530, "miny": -151.46, "maxy": -136.739},  # usable下緣橫條
    "west":  {"minx": 389.119, "maxx": 403.669, "miny": -136.739, "maxy": -81.54},    # usable左側直條
    "north": {"minx": 403.669, "maxx": 431.530, "miny": -81.54, "maxy": -91.865},     # usable上緣橫條
    "east":  {"minx": 416.980, "maxx": 431.530, "miny": -136.739, "maxy": -91.865},   # usable右側直條
}

# === 4. 條帶分割自動切（方向/順序已根據你需求）===
def proportional_strip(zone_rows, minx, maxx, miny, maxy, usable_poly, direction='vertical'):
    S = usable_poly.area
    total_target = sum(row[1] for row in zone_rows)
    real_areas = [row[1] * S / total_target for row in zone_rows] if total_target else [0]*len(zone_rows)
    strips = {}
    current = minx if direction == 'vertical' else miny
    for idx, row in enumerate(zone_rows):
        name = row[0]
        target_area = real_areas[idx]
        if idx < len(zone_rows)-1:
            low, high = current, maxx if direction == 'vertical' else maxy
            for _ in range(50):
                mid = (low + high)/2
                if direction == 'vertical':
                    band = Polygon([(current, miny), (mid, miny), (mid, maxy), (current, maxy)])
                else:
                    band = Polygon([(minx, current), (maxx, current), (maxx, mid), (minx, mid)])
                part = band.intersection(usable_poly)
                area = part.area
                if abs(area - target_area) < 2.0:
                    break
                if area < target_area:
                    low = mid
                else:
                    high = mid
            strip_poly = band.intersection(usable_poly)
            strips[name] = strip_poly
            usable_poly = usable_poly.difference(strip_poly)
            current = mid
        else:
            strips[name] = usable_poly
    return strips

output_zones = {}

# 南方條帶（左到右）：vertical
rows_south = [row for row in spaces if row[4]=="south"]
cfg = zones_config["south"]
zone_box = Polygon([(cfg["minx"], cfg["miny"]), (cfg["maxx"], cfg["miny"]), (cfg["maxx"], cfg["maxy"]), (cfg["minx"], cfg["maxy"])])
usable_zone = zone_box.intersection(usable)
output_zones.update(proportional_strip(rows_south, cfg["minx"], cfg["maxx"], cfg["miny"], cfg["maxy"], usable_zone, direction='vertical'))

# 西方條帶（上到下）：horizontal
rows_west = [row for row in spaces if row[4] == "west"][::-1]
cfg = zones_config["west"]
zone_box = Polygon([(cfg["minx"], cfg["miny"]), (cfg["maxx"], cfg["miny"]), (cfg["maxx"], cfg["maxy"]), (cfg["minx"], cfg["maxy"])])
usable_zone = zone_box.intersection(usable)
output_zones.update(proportional_strip(rows_west, cfg["minx"], cfg["maxx"], cfg["miny"], cfg["maxy"], usable_zone, direction='horizontal'))

# 北方條帶（左到右）：vertical
rows_north = [row for row in spaces if row[4]=="north"]
cfg = zones_config["north"]
zone_box = Polygon([(cfg["minx"], cfg["miny"]), (cfg["maxx"], cfg["miny"]), (cfg["maxx"], cfg["maxy"]), (cfg["minx"], cfg["maxy"])])
usable_zone = zone_box.intersection(usable)
output_zones.update(proportional_strip(rows_north, cfg["minx"], cfg["maxx"], cfg["miny"], cfg["maxy"], usable_zone, direction='vertical'))

# 東方條帶（上到下）：horizontal
rows_east = [row for row in spaces if row[4] == "east"][::-1]
cfg = zones_config["east"]
zone_box = Polygon([(cfg["minx"], cfg["miny"]), (cfg["maxx"], cfg["miny"]), (cfg["maxx"], cfg["maxy"]), (cfg["minx"], cfg["maxy"])])
usable_zone = zone_box.intersection(usable)
output_zones.update(proportional_strip(rows_east, cfg["minx"], cfg["maxx"], cfg["miny"], cfg["maxy"], usable_zone, direction='horizontal'))

# 多邊形合法化
def safe_export_poly(poly):
    final_poly = None
    if poly.is_empty: return None
    if poly.geom_type == "Polygon": final_poly = poly
    elif poly.geom_type == "MultiPolygon":
        polys = [p for p in poly.geoms if not p.is_empty and p.area > 1e-3]
        if polys: final_poly = max(polys, key=lambda p: p.area)
    elif poly.geom_type == "GeometryCollection":
        polys = [g for g in poly.geoms if g.geom_type == "Polygon" and not g.is_empty and g.area > 1e-3]
        if polys: final_poly = max(polys, key=lambda p: p.area)
    if not final_poly: return None
    final_poly = final_poly.simplify(0.001, preserve_topology=True)
    if not final_poly.is_valid:
        final_poly = final_poly.buffer(0)
    if not final_poly.is_valid:
        print("警告：polygon 仍然非法：", explain_validity(final_poly))
        return None
    coords = list(final_poly.exterior.coords)
    return [[float(x), float(y), 0] for x, y in coords]

output = {}
diff_total = 0.0
for row in spaces:
    name, area, color, eng, zone = row
    poly = output_zones.get(name)
    pts3d = safe_export_poly(poly)
    if not pts3d:
        print(f"警告：{name} 找不到有效多邊形")
        continue
    output[name] = {"type": "polyline", "data": {"points": pts3d}}
    output[f"{name}_color"] = {"type": "color", "data": color}
    output[f"{name}_function"] = {name: eng}
    poly2d = Polygon([pt[:2] for pt in pts3d])
    diff = poly2d.area - area
    diff_total += diff
    print(f"{name}: target={area:.2f}, actual={poly2d.area:.2f}, diff={diff:.2f}")
print(f"==== 總誤差 sum(diff) = {diff_total:.2f}㎡ ====")

with open('內聚式社區學習核心.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("zone_your_new_strips.json 完成！")
