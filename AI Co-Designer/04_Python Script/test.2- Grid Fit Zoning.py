import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
import json

# 1. 輪廓
outline_pts = [
    [251.3241, -140.0428], [251.3241, -90.2209], [255.5068, -90.2209],
    [255.5068, -82.4483], [217.4709, -82.4483], [217.4709, -80.9398],
    [208.3137, -80.9398], [208.3137, -151.4619], [236.8940, -151.4619],
    [236.8940, -140.8481], [251.3241, -140.8481], [251.3241, -140.0428]
]
outline = Polygon([pt[:2] for pt in outline_pts])

# 2. 格線
raw_nodes = [
    [208.3137, -92.6667], [219.2581, -92.6667], [223.2439, -92.6667], [236.3940, -92.6667], [240.3797, -92.6667], [251.3241, -92.6667],
    [208.3137, -102.0492], [219.2581, -102.0492], [223.2439, -102.0492], [236.3940, -102.0492], [240.3797, -102.0492], [251.3241, -102.0492],
    [208.3137, -111.4316], [219.2581, -111.4316], [223.2439, -111.4316], [236.3940, -111.4316], [240.3797, -111.4316], [251.3241, -111.4316],
    [208.3137, -120.8140], [219.2581, -120.8140], [223.2439, -120.8140], [236.3940, -120.8140], [240.3797, -120.8140], [251.3241, -120.8140],
    [208.3137, -130.1965], [219.2581, -130.1965], [223.2439, -130.1965], [236.3940, -130.1965], [240.3797, -130.1965], [251.3241, -130.1965],
    [219.2581, -82.4483], [223.2439, -82.4483], [236.3940, -82.4483], [240.3797, -82.4483], [240.3797, -140.8481], [236.3940, -140.8481], 
    [223.2439, -140.8481], [219.2581, -140.8481], [208.3137, -140.8481], [219.2581, -151.4619], [223.2439, -151.4619]
]
xlist = sorted(list(set([round(pt[0], 4) for pt in raw_nodes])))
ylist = sorted(list(set([round(pt[1], 4) for pt in raw_nodes])), reverse=True)
cells = []
for ix in range(len(xlist) - 1):
    for iy in range(len(ylist) - 1):
        pts = [
            (xlist[ix], ylist[iy]),
            (xlist[ix + 1], ylist[iy]),
            (xlist[ix + 1], ylist[iy + 1]),
            (xlist[ix], ylist[iy + 1])
        ]
        cell = Polygon(pts)
        poly = outline.intersection(cell)
        if poly.area > 1e-2:
            cells.append(poly)

def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip("#")
    return [int(hexcode[i:i+2], 16) for i in (0, 2, 4)]

# 你的專案空間設定（紅色為#E94F37，可調為你要的紅色HEX）
space_defs = [
     ("0", "South", "#71A8F0", 5),
      ("Cooking Room", "South", "#71A8F0", 220),
    ("Elderly Daycare Center", "East-Mid/Northeast", "#E94F37", 500),   # 1. 東邊，紅色
    ("Entrance Lobby", "West Center", "#243CF0", 190),                  # 2. 西中
                             # 3. 南邊
    # 其餘空間順序任意
    ("Art & DIY Classroom", "Southwest Corner", "#71A8F0", 150),
    ("Social Lounge", "South", "#71A8F0", 170),
    ("Salon", "West-North", "#D322F0", 65),
    ("Café", "West-South", "#D322F0", 125),
    ("Gallery & Community Shop", "West-Southernmost", "#243CF0", 145),
    ("Office", "North Band", "#616161", 210),
    ("Public Toilet", "Northeast Corner", "#616161", 50),
    ("Animal Therapy Zone", "East", "#A1CFA5", 125),
    ("Dining Room", "East-South", "#71A8F0", 190),
    ("Dance Hall", "Center", "#71A8F0", 165),
    ("Open Lecture Hall", "Center", "#243CF0", 155),
    ("Video Hall", "NE / Center-North", "#71A8F0", 135),
    ("Library & Reading Lounge", "West / Central Link", "#243CF0", 70),
    ("IT & Digital Learning Room", "Near Lecture / Library", "#243CF0", 50),
    ("Family Visit Room / Lounge", "Near Daycare / East", "#A1CFA5", 40),
    ("Volunteer / Staff Room", "Near Office", "#616161", 35),
    ("Sensory Room", "Near Daycare / Quiet", "#A1CFA5", 60),
    ("Multipurpose Room A", "Near Lecture Hall", "#71A8F0", 125),
    ("Multipurpose Room B", "Near Café / Community", "#71A8F0", 125)
]

# 依你這張表不用scale！
cell_centers = [cell.centroid.coords[0] for cell in cells]
MAX_ROUNDS = 10

static_spaces = space_defs[:3]  # 固定前3個
variable_spaces_init = space_defs[3:]
best_area_log = None
best_output = None
best_max_diff = 1e9

def region_score(center, orient):
    x, y = center
    minx, miny, maxx, maxy = outline.bounds
    mx = (minx + maxx) / 2
    my = (miny + maxy) / 2
    score = 0
    orient = orient.lower()
    if "south" in orient:
        score = (maxy - y) * 2
    elif"southwest" in orient:
        score = (x - minx) * 2 + (maxy - y)
    elif "west-north" in orient:
        score = (x - minx) * 2 + (y - miny)
    elif "west-south" in orient:
        score = (x - minx) * 2 + (maxy - y)
    elif "west center" in orient:
        score = (x - minx) * 2 + abs(y - my)
    elif "west" in orient:
        score = (x - minx) * 2
    elif "east" in orient:
        score = (maxx - x) * 2
    elif "south" in orient:
        score = (maxy - y) * 2
    elif "north" in orient:
        score = (y - miny) * 2
    elif "center" in orient:
        score = abs(x - mx) + abs(y - my)
    else:
        score = 0
    return score

for round_id in range(MAX_ROUNDS):
    variable_spaces = variable_spaces_init.copy()
    output = {}
    area_log = []
    occupied_poly = Polygon()
    fail_list = []

    all_spaces = static_spaces + variable_spaces

    for idx, (ename, orient, hexcode, target_area) in enumerate(all_spaces):
        available_outline = outline.difference(occupied_poly)
        # 格線拼合
        scores = [(i, region_score(cell_centers[i], orient)) for i in range(len(cells)) if not cells[i].intersection(available_outline).is_empty]
        scores = sorted(scores, key=lambda t: t[1])
        chosen = []
        total_area = 0
        for i, _ in scores:
            cell_avail = cells[i].intersection(available_outline)
            area = cell_avail.area
            if area > 1e-2 and total_area < target_area and occupied_poly.intersection(cell_avail).area < 1e-5:
                chosen.append(cell_avail)
                total_area += area
            if abs(total_area - target_area) < 10:
                break
        union_poly = unary_union(chosen) if chosen else Polygon()

        # 補塊（完全防重疊！）
        diff = abs(union_poly.area - target_area)
        if diff >= 10 or union_poly.is_empty:
            minx, miny, maxx, maxy = available_outline.bounds
            direction = orient.lower()
            for scale in np.arange(1, 1.6, 0.01):
                width = (target_area)**0.5 * scale
                height = target_area / width
                if "south" in direction and "west" in direction:
                    x0 = minx
                    y0 = miny
                elif "south" in direction and "east" in direction:
                    x0 = maxx - width
                    y0 = miny
                elif "north" in direction and "west" in direction:
                    x0 = minx
                    y0 = maxy - height
                elif "north" in direction and "east" in direction:
                    x0 = maxx - width
                    y0 = maxy - height
                elif "south" in direction:
                    x0 = (minx + maxx) / 2 - width / 2
                    y0 = miny
                elif "north" in direction:
                    x0 = (minx + maxx) / 2 - width / 2
                    y0 = maxy - height
                elif "west" in direction:
                    x0 = minx
                    y0 = (miny + maxy) / 2 - height / 2
                elif "east" in direction:
                    x0 = maxx - width
                    y0 = (miny + maxy) / 2 - height / 2
                else:  # center
                    x0 = (minx + maxx) / 2 - width / 2
                    y0 = (miny + maxy) / 2 - height / 2
                rect = Polygon([(x0, y0), (x0+width, y0), (x0+width, y0+height), (x0, y0+height)])
                poly_cand = available_outline.intersection(rect)
                if poly_cand.is_empty or poly_cand.area < 1e-2:
                    continue
                if poly_cand.geom_type == "MultiPolygon":
                    pieces = [p for p in poly_cand.geoms if p.area > 1e-2 and occupied_poly.intersection(p).area < 1e-5]
                    if not pieces:
                        continue
                    poly = max(pieces, key=lambda p: p.area)
                else:
                    if occupied_poly.intersection(poly_cand).area < 1e-5:
                        poly = poly_cand
                    else:
                        continue
                diff2 = abs(poly.area - target_area)
                if poly.area > 1e-2 and diff2 < 10:
                    union_poly = poly
                    diff = diff2
                    break

        if union_poly.is_empty or union_poly.area < 1e-2:
            fail_list.append((ename, orient, hexcode, target_area))
            continue
        if union_poly.geom_type == "MultiPolygon":
            poly = max(union_poly.geoms, key=lambda p: p.area)
        elif union_poly.geom_type == "Polygon":
            poly = union_poly
        else:
            fail_list.append((ename, orient, hexcode, target_area))
            continue
        coords = list(poly.exterior.coords)
        pts3d = [[float(x), float(y), 0] for x, y in coords]
        key = chr(65+idx)
        color = hex_to_rgb(hexcode)
        output[key] = {"type": "polyline", "data": {"points": pts3d}}
        output[f"{key}_color"] = {"type": "color", "data": color}
        output[f"{key}_function"] = {key: ename}
        area_log.append((key, ename, target_area, poly.area, poly.area - target_area))
        occupied_poly = unary_union([occupied_poly, poly])

    # 有diff>30的空間全部丟到隊尾（但前3名永遠不動！）
    move_list = []
    for rec in area_log[3:]:  # 只針對可動空間
        if abs(rec[4]) > 30:
            move_list.append(rec[1])
    if not move_list:
        best_area_log = area_log
        best_output = output
        break
    # 重新排序，把大誤差推到最後再排
    to_resort = []
    rest = []
    for s in variable_spaces_init:
        if s[0] in move_list:
            to_resort.append(s)
        else:
            rest.append(s)
    variable_spaces_init = rest + to_resort
    this_max_diff = max(abs(rec[4]) for rec in area_log)
    if this_max_diff < best_max_diff:
        best_max_diff = this_max_diff
        best_area_log = area_log
        best_output = output
    else:
        break

print("Space,Ideal,Actual,Diff")
sum_diff = 0
for k, name, ideal, actual, diff in best_area_log:
    print(f"{name},{ideal:.2f},{actual:.2f},{diff:.2f}")
    sum_diff += diff
print(f"sum(diff): {sum_diff:.2f}")
if all(abs(rec[4])<=30 for rec in best_area_log):
    print("🎉 All spaces diff ≤ 30㎡")
else:
    print("⚠️ Some spaces diff > 30㎡")
with open('9.json', 'w', encoding='utf-8') as f:
    json.dump(best_output, f, ensure_ascii=False, indent=2)
print("✅ layout_gridfit_superorder.json 產生完成")
