import json
import math
import random
from shapely.geometry import Polygon, Point, box

boundary_pts = [
    [17.912512227017373, 140.35318242529189],
    [17.912512227017373, 136.37868674857344],
    [16.322713956329949, 136.37868674857344],
    [16.322713956330063, 107.76774248586884],
    [50.900826343780409, 107.76774248586884],
    [50.900826343780409, 116.40624979871183],
    [53.408998082168182, 116.40624979871183],
    [53.408998082168182, 130.74841617293413],
    [50.900826343780409, 130.74841617293413],
    [50.900826343780409, 140.35318242529189],
    [17.912512227017373, 140.35318242529189]
]
poly = Polygon(boundary_pts)
main_y = 107.76774248586884
close_band = 3.0

def tag(floor, count):
    return f"{floor}{chr(65+count)}"

def rectangle_points(cx, cy, w, h, z):
    return [
        [cx-w/2, cy-h/2, z],
        [cx+w/2, cy-h/2, z],
        [cx+w/2, cy+h/2, z],
        [cx-w/2, cy+h/2, z],
        [cx-w/2, cy-h/2, z]
    ]

def rect_within_poly(pts, poly):
    return all(poly.contains(Point(x, y)) for x, y, z in pts)

def rects_overlap_2d(r1, r2):
    b1 = box(min([p[0] for p in r1]), min([p[1] for p in r1]), max([p[0] for p in r1]), max([p[1] for p in r1]))
    b2 = box(min([p[0] for p in r2]), min([p[1] for p in r2]), max([p[0] for p in r2]), max([p[1] for p in r2]))
    return b1.intersects(b2)

def rects_overlap(r1, r2):
    xs1 = [p[0] for p in r1]
    ys1 = [p[1] for p in r1]
    xs2 = [p[0] for p in r2]
    ys2 = [p[1] for p in r2]
    if max(xs1) <= min(xs2) or min(xs1) >= max(xs2) or max(ys1) <= min(ys2) or min(ys1) >= max(ys2):
        return False
    return True

def center_distance(c1, c2):
    return math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)

with open('AddLifespace_8F_13F_with_more_treebox.json', 'r', encoding='utf-8') as f:
    spaces = json.load(f)

floors = {}
for s in spaces:
    floor = s['Floor'].replace('F', '')
    if floor not in floors:
        floors[floor] = []
    floors[floor].append(s)

json_result = {}
outdoor_mask = {}
treebox_xy_by_floor = {}
sorted_floors = sorted([int(f) for f in floors.keys()])

# 計算最大空間尺寸
all_ws = [math.sqrt(float(s['Area(m2)'])*2) for s in spaces]
all_hs = [math.sqrt(float(s['Area(m2)'])*2)/2 for s in spaces]
max_w = max(all_ws)
max_h = max(all_hs)
buffer_dist = max(max_w, max_h) / 2
safe_poly = poly.buffer(-buffer_dist)
print("Safe polygon area:", safe_poly.area)

treebox_w = 4.0
treebox_h = 4.0
treebox_min_dist = 7.0

for i, floor_int in enumerate(sorted_floors):
    floor = str(floor_int)
    used_rects = []
    centers = []
    treebox_rects_this_floor = []
    treebox_centers_this_floor = []
    z = float(floor) * 3.7
    count = 0
    mask_rects = []
    if i > 0:
        lower_floor = str(sorted_floors[i-1])
        mask_rects = outdoor_mask.get(lower_floor, [])
    minx, miny, maxx, maxy = safe_poly.bounds

    print(f"--- Floor {floor} ({len(floors[floor])} spaces) ---")

    # 只保留本層前N個Tree Box，其餘跳過
    treebox_spaces = [s for s in floors[floor] if "tree box" in s["Space Name"].lower()]
    # 8F 兩個，其它一個，13F不要
    treebox_count = 0
    if floor == "13":
        max_treebox = 0
    elif floor == "8":
        max_treebox = 2
    else:
        max_treebox = 1
    treebox_spaces = treebox_spaces[:max_treebox]
    other_spaces = [s for s in floors[floor] if "tree box" not in s["Space Name"].lower()]

    # y軸分區
    num_treebox = len(treebox_spaces)
    y_sections = num_treebox if num_treebox>0 else 1
    section_height = (maxy - main_y) / y_sections

    for idx, space in enumerate(treebox_spaces):
        w, h = treebox_w, treebox_h
        min_y_this = main_y + idx*section_height
        max_y_this = main_y + (idx+1)*section_height - h/2
        best_cx, best_cy = None, None
        best_min_dist = -1
        found = False
        for try_outer in range(20):
            candidates = []
            for _ in range(40):
                inner_tries = 0
                while True:
                    rndx = random.uniform(minx, maxx)
                    rndy = random.uniform(min_y_this + h/2, max_y_this)
                    if safe_poly.contains(Point(rndx, rndy)):
                        cx, cy = rndx, rndy
                        break
                    inner_tries += 1
                    if inner_tries > 200:
                        cx, cy = minx, min_y_this + h/2
                        break
                pts = rectangle_points(cx, cy, w, h, z)
                conflict = False
                for df in [-1, 1]:
                    neighbor_floor = str(floor_int + df)
                    for r in treebox_xy_by_floor.get(neighbor_floor, []):
                        if rects_overlap_2d(pts, r):
                            conflict = True
                            break
                    if conflict:
                        break
                for r in treebox_rects_this_floor:
                    if rects_overlap_2d(pts, r):
                        conflict = True
                        break
                for c in treebox_centers_this_floor:
                    if center_distance((cx, cy), c) < treebox_min_dist:
                        conflict = True
                        break
                if not conflict and rect_within_poly(pts, poly):
                    min_dist = min([center_distance((cx, cy), c) for c in treebox_centers_this_floor], default=9999)
                    candidates.append((min_dist, cx, cy, pts))
            if candidates:
                candidates.sort(reverse=True)
                _, cx, cy, pts = candidates[0]
                found = True
                break
        if not found:
            print(f"【警告】{space['Space Name']} 在 {floor}F 找不到不重疊且分散位置，請檢查空間數或尺寸！")
            cx, cy = minx, min_y_this + h/2
            pts = rectangle_points(cx, cy, w, h, z)
        t = tag(floor, count)
        color = "#22C55E"
        json_result[t] = {
            "type": "polyline",
            "data": {"points": pts}
        }
        json_result[f"{t}_semi-outdoor"] = "3.7" if space['Type'].lower() == "semi-outdoor" else "0"
        json_result[f"{t}_indoor"] = "11.1"
        json_result[f"{t}_function"] = space["Space Name"]
        json_result[f"{t}_color"] = color
        used_rects.append(pts)
        treebox_rects_this_floor.append(pts)
        treebox_centers_this_floor.append((cx, cy))
        centers.append((cx, cy))
        count += 1
    treebox_xy_by_floor[floor] = treebox_rects_this_floor

    # 其餘空間
    for space in other_spaces:
        area = float(space['Area(m2)'])
        w = math.sqrt(area * 2)
        h = w / 2
        tip = space.get("Attachment Suggestion", "")
        if "靠近" in tip:
            min_y_this = main_y
            max_y_this = main_y + close_band
        elif "遠離" in tip or "自由" in tip:
            min_y_this = main_y + close_band + 1
            max_y_this = maxy - h/2
        else:
            min_y_this = main_y
            max_y_this = maxy - h/2

        best_cx, best_cy = None, None
        best_min_dist = -1
        found = False
        for try_outer in range(10):
            candidates = []
            for _ in range(8):
                inner_tries = 0
                while True:
                    rndx = random.uniform(minx, maxx)
                    rndy = random.uniform(min_y_this + h/2, max_y_this - h/2)
                    if safe_poly.contains(Point(rndx, rndy)):
                        cx, cy = rndx, rndy
                        break
                    inner_tries += 1
                    if inner_tries > 100:
                        cx, cy = minx, min_y_this + h/2
                        break
                pts = rectangle_points(cx, cy, w, h, z)
                if rect_within_poly(pts, poly) and all(not rects_overlap(pts, r) for r in used_rects) and all(not rects_overlap(pts, r) for r in mask_rects):
                    min_dist = min([center_distance((cx, cy), c) for c in centers], default=9999)
                    candidates.append((min_dist, cx, cy, pts))
            if candidates:
                candidates.sort(reverse=True)
                _, cx, cy, pts = candidates[0]
                found = True
                break
        if not found:
            cx, cy = minx, min_y_this + h/2
            pts = rectangle_points(cx, cy, w, h, z)
            print(f"警告：{space['Space Name']} 在樓層 {floor} 找不到分散安全位置，已強制隨機放入（可能小重疊/貼邊）")
        t = tag(floor, count)
        tags = " ".join(space.get("Semantic Tags", []))
        if "社交活動串連" in tags:
            color = "#EF4444"
        elif ("視覺串連" in tags or "自然通感節點" in tags or "錯層對看" in tags):
            color = "#3B82F6"
        else:
            color = "#FFFFFF"
        json_result[t] = {
            "type": "polyline",
            "data": {"points": pts}
        }
        json_result[f"{t}_semi-outdoor"] = "3.7" if space['Type'].lower() == "semi-outdoor" else "0"
        json_result[f"{t}_indoor"] = "3.7" if space['Type'].lower() == "indoor" else "0"
        json_result[f"{t}_function"] = space["Space Name"]
        json_result[f"{t}_color"] = color
        used_rects.append(pts)
        centers.append((cx, cy))
        if space['Type'].lower() == "outdoor":
            if floor not in outdoor_mask:
                outdoor_mask[floor] = []
            outdoor_mask[floor].append(pts)
        count += 1

with open('spaces_polyline_treebox_1perfloor.json', 'w', encoding='utf-8') as f:
    json.dump(json_result, f, ensure_ascii=False, indent=2)

print('全部完成！每層最多一個Tree Box（8F兩個，13F沒有），其它空間正常分布，請檢查 spaces_polyline_treebox_1perfloor.json')
