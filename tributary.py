import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import polygonize, unary_union

# --- Load data ---
points_df = pd.read_csv("dxf_points.csv")
boundary_df = pd.read_csv("dxf_boundaries.csv")

# --- Reconstruct slab boundary ---
boundary_lines = [
    LineString([(row['start_x'], row['start_y']), (row['end_x'], row['end_y'])])
    for _, row in boundary_df.iterrows()
]
slab_polygon = list(polygonize(unary_union(boundary_lines)))[0].buffer(0.006)

# --- Bounding box for region generation ---
minx, miny, maxx, maxy = slab_polygon.bounds
bbox = {'minx': minx - 5, 'maxx': maxx + 5, 'miny': miny - 5, 'maxy': maxy + 5}

def half_plane_polygon(P, Q, bbox):
    Px, Py, Qx, Qy = P.x, P.y, Q.x, Q.y
    A = Qx - Px
    B = Qy - Py
    C = (Qx**2 + Qy**2 - Px**2 - Py**2) / 2.0
    corners = [(bbox['minx'], bbox['miny']), (bbox['maxx'], bbox['miny']),
               (bbox['maxx'], bbox['maxy']), (bbox['minx'], bbox['maxy'])]
    pts = [(cx, cy) for (cx, cy) in corners if A*cx + B*cy <= C + 1e-9]
    if abs(B) < 1e-9 and abs(A) > 1e-9:
        x0 = C / A
        if bbox['minx'] <= x0 <= bbox['maxx']:
            pts += [(x0, bbox['miny']), (x0, bbox['maxy'])]
    if abs(A) < 1e-9 and abs(B) > 1e-9:
        y0 = C / B
        if bbox['miny'] <= y0 <= bbox['maxy']:
            pts += [(bbox['minx'], y0), (bbox['maxx'], y0)]
    if abs(B) > 1e-9:
        for y0 in [bbox['miny'], bbox['maxy']]:
            x0 = (C - B*y0) / A if abs(A) > 1e-9 else None
            if x0 and bbox['minx'] <= x0 <= bbox['maxx']:
                pts.append((x0, y0))
    if abs(A) > 1e-9:
        for x0 in [bbox['minx'], bbox['maxx']]:
            y0 = (C - A*x0) / B if abs(B) > 1e-9 else None
            if y0 and bbox['miny'] <= y0 <= bbox['maxy']:
                pts.append((x0, y0))
    if len(pts) < 3:
        return None
    return Polygon(pts).convex_hull

# --- Compute tributary regions ---
column_points = [Point(x, y) for x, y in zip(points_df['x'], points_df['y'])]
regions = []
for i, P in enumerate(column_points):
    region = slab_polygon
    for j, Q in enumerate(column_points):
        if i == j: continue
        hp = half_plane_polygon(P, Q, bbox)
        if hp:
            region = region.intersection(hp)
        if region.is_empty: break
    regions.append(region)

# --- Find and highlight largest 12 area regions ---
areas = [r.area for r in regions]
largest_idxs = sorted(range(len(areas)), key=lambda i: areas[i], reverse=True)[:12]
print("Largest 12 tributary areas:")
for rank, idx in enumerate(largest_idxs, 1):
    print(f"{rank}. Column {idx} at ({points_df['x'][idx]:.2f}, {points_df['y'][idx]:.2f}): {areas[idx]:.2f} sq ft")

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 6))

# Plot slab boundary
x, y = slab_polygon.exterior.xy
ax.plot(x, y, 'k-', label='Slab boundary')

# Plot column points
ax.scatter(points_df['x'], points_df['y'], color='black', zorder=5, label='Columns')

# Plot tributary regions
for i, region in enumerate(regions):
    if region.is_empty: continue
    if i in largest_idxs:
        color = 'orange'
        edge = 'red'
    else:
        color = 'skyblue'
        edge = 'blue'
    ax.add_patch(plt.Polygon(region.exterior.coords, facecolor=color, edgecolor=edge, alpha=0.4))
    # Annotate area for largest 12
    if i in largest_idxs:
        centroid = region.centroid
        ax.text(centroid.x, centroid.y, f"{areas[i]:.1f} sf", color='red', fontsize=10, ha='center', va='center', fontweight='bold')

ax.set_title("Tributary Areas (Largest 12 Highlighted)")
ax.set_aspect('equal')
ax.legend()
plt.xlabel("X (ft)")
plt.ylabel("Y (ft)")
plt.tight_layout()
plt.show()