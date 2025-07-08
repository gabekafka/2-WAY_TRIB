import pandas as pd
import matplotlib.pyplot as plt

# Load the point data from CSV
points_df = pd.read_csv("dxf_points.csv")

# Load the boundary data
try:
    boundaries_df = pd.read_csv("dxf_boundaries.csv")
except FileNotFoundError:
    boundaries_df = pd.DataFrame()

# Preview the first few rows of each
print("✅ POINTS CSV:")
print(points_df.head())

if not boundaries_df.empty:
    print("\n✅ BOUNDARIES CSV:")
    print(boundaries_df.head())
else:
    print("\n⚠️ No boundaries found in dxf_boundaries.csv.")

# Plot points
plt.scatter(points_df['x'], points_df['y'], color='blue', label='Points')

# Plot boundaries (polylines/lwpolylines and lines)
if not boundaries_df.empty:
    # Plot polyline boundaries
    poly_df = boundaries_df[boundaries_df['type'].isin(['POLYLINE', 'LWPOLYLINE'])]
    for boundary_id, group in poly_df.groupby('boundary_id'):
        x = group.sort_values('vertex_index')['x'].values
        y = group.sort_values('vertex_index')['y'].values
        closed = group['closed'].iloc[0] if 'closed' in group else False
        if closed:
            # Close the polyline
            x = list(x) + [x[0]]
            y = list(y) + [y[0]]
        plt.plot(x, y, color='green', linewidth=2, linestyle='--', label='Boundary' if boundary_id == poly_df['boundary_id'].min() else "")
    
    # Plot line boundaries
    line_df = boundaries_df[boundaries_df['type'] == 'LINE']
    for idx, row in line_df.iterrows():
        x_values = [row['start_x'], row['end_x']]
        y_values = [row['start_y'], row['end_y']]
        plt.plot(x_values, y_values, color='green', linewidth=2, linestyle='--', label='Boundary' if idx == line_df.index[0] else "")

plt.xlabel('X (ft)')
plt.ylabel('Y (ft)')
plt.title('Points and Boundaries Visualization')
plt.legend()
plt.axis('equal')
plt.show()