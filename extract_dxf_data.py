import ezdxf
import pandas as pd
import numpy as np

# Conversion factor
INCHES_TO_FEET = 1/12

# Load the DXF file
doc = ezdxf.readfile("POINTS AND LINES FOR TRIBUTARY.dxf")
msp = doc.modelspace()

# Initialize storage
points = []
boundaries = []

# Extract entities, using layers to distinguish types
for e in msp:
    layer = e.dxf.layer if hasattr(e.dxf, 'layer') else ''
    if e.dxftype() == "POINT":
        pt = e.dxf.location
        points.append((pt.x * INCHES_TO_FEET, pt.y * INCHES_TO_FEET))
    elif e.dxftype() == "LINE" and layer == 'BOUNDARY':
        start = e.dxf.start
        end = e.dxf.end
        boundaries.append({
            'type': 'LINE',
            'start': (start.x * INCHES_TO_FEET, start.y * INCHES_TO_FEET),
            'end': (end.x * INCHES_TO_FEET, end.y * INCHES_TO_FEET)
        })
    elif e.dxftype() in ["POLYLINE", "LWPOLYLINE"] and layer == 'BOUNDARY':
        # Extract polyline vertices
        vertices = []
        if e.dxftype() == "POLYLINE":
            for vertex in e.vertices:
                pt = vertex.dxf.location
                vertices.append((pt.x * INCHES_TO_FEET, pt.y * INCHES_TO_FEET))
        else:  # LWPOLYLINE
            for vertex in e.get_points():
                vertices.append((vertex[0] * INCHES_TO_FEET, vertex[1] * INCHES_TO_FEET))
        if vertices:
            boundaries.append({
                'type': e.dxftype(),
                'vertices': vertices,
                'closed': e.closed if hasattr(e, 'closed') else False
            })
    elif e.dxftype() == "CIRCLE" and layer == 'BOUNDARY':
        center = e.dxf.center
        radius = e.dxf.radius
        boundaries.append({
            'type': 'CIRCLE',
            'center': (center.x * INCHES_TO_FEET, center.y * INCHES_TO_FEET),
            'radius': radius * INCHES_TO_FEET
        })
    elif e.dxftype() == "ARC" and layer == 'BOUNDARY':
        center = e.dxf.center
        radius = e.dxf.radius
        start_angle = e.dxf.start_angle
        end_angle = e.dxf.end_angle
        boundaries.append({
            'type': 'ARC',
            'center': (center.x * INCHES_TO_FEET, center.y * INCHES_TO_FEET),
            'radius': radius * INCHES_TO_FEET,
            'start_angle': start_angle,
            'end_angle': end_angle
        })

# Convert to DataFrames
points_df = pd.DataFrame(points, columns=["x", "y"])

# Create boundaries DataFrame
boundary_data = []
for i, boundary in enumerate(boundaries):
    if boundary['type'] in ["POLYLINE", "LWPOLYLINE"]:
        for j, vertex in enumerate(boundary['vertices']):
            boundary_data.append({
                'boundary_id': i,
                'type': boundary['type'],
                'vertex_index': j,
                'x': vertex[0],
                'y': vertex[1],
                'closed': boundary['closed']
            })
    elif boundary['type'] == "LINE":
        boundary_data.append({
            'boundary_id': i,
            'type': 'LINE',
            'start_x': boundary['start'][0],
            'start_y': boundary['start'][1],
            'end_x': boundary['end'][0],
            'end_y': boundary['end'][1]
        })
    elif boundary['type'] == "CIRCLE":
        boundary_data.append({
            'boundary_id': i,
            'type': boundary['type'],
            'center_x': boundary['center'][0],
            'center_y': boundary['center'][1],
            'radius': boundary['radius']
        })
    elif boundary['type'] == "ARC":
        boundary_data.append({
            'boundary_id': i,
            'type': boundary['type'],
            'center_x': boundary['center'][0],
            'center_y': boundary['center'][1],
            'radius': boundary['radius'],
            'start_angle': boundary['start_angle'],
            'end_angle': boundary['end_angle']
        })

boundaries_df = pd.DataFrame(boundary_data)

# Save to CSV
points_df.to_csv("dxf_points.csv", index=False)
boundaries_df.to_csv("dxf_boundaries.csv", index=False)

print("Points:")
print(points_df)
print("\nBoundaries:")
print(boundaries_df)