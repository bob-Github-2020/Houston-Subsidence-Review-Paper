#!/usr/bin/python3
## 9-26-2024, plots a single plot

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from pykrige.ok import OrdinaryKriging
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.cm as cm  # Function to calculate the area within a contour
from matplotlib.path import Path
from shapely.geometry import Polygon
from matplotlib.lines import Line2D


def calculate_contour_area(collection):
    total_area = 0.0
    for path in collection.get_paths():
        vertices = path.vertices
        poly = Polygon(vertices)
        # Convert degrees^2 to km^2 (assuming 111 km per degree of latitude at the equator)
        area = poly.area * (111 ** 2)
        total_area += area
    return total_area



# File with data for the 2020-2024 period
file = 'Houston_Wells_LL_GWL_2020-2024.lld'

# Read county shape data and prepare Loop 610 data
counties = gpd.read_file('County.shp').to_crs("EPSG:4326")
loop610 = pd.read_csv('Houston_IH610_inner_loop.psxy', delimiter=' ', header=0)

# Load GPS-recorded subsidence data
gps_data = pd.read_csv('subsidence_rates_2019-2023.txt', delimiter=' ', header=None, names=['Longitude', 'Latitude', 'Subsidence_Rate', 'Site_ID'])

# Load extensometer data
extensometer_data = pd.read_csv('Extensometers.psxy', delimiter=' ', header=None, names=['Longitude', 'Latitude', 'Depth', 'Site_ID'])

   
# Function to calculate the area within a contour
def calculate_contour_area(collection):
    total_area = 0.0
    for path in collection.get_paths():
        vertices = path.vertices
        poly = Polygon(vertices)
        # Convert degrees^2 to km^2 (assuming 111 km per degree of latitude at the equator)
        area = poly.area * (111 ** 2)
        total_area += area
    return total_area
    
# Well_Depth_BLS is positive numbers
def standardize_gwl(row, ivhg=-0.07, target_depth=300):
    # Calculate depth difference
    depth_diff = target_depth - row['Well_Depth_BLS']
    # Adjust GWL_Median based on IVHG and depth difference
    row['GWL_Median'] = round(row['GWL_Median'] + depth_diff * ivhg, 1)
    return row

# Create a single plot
fig, ax = plt.subplots(figsize=(10, 14))

# Adjust the position of the plot to move it up and create more space at the bottom
plt.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.2)  # Increase the 'bottom' value to move the plot up

# Set x and y limits
ax.set_xlim([-96, -94.7])
ax.set_ylim([29.1, 30.4])

# Load data from the current file
org_df = pd.read_csv(file, delimiter='\t', names=['Longitude', 'Latitude', 'GWL_Median', 'Well_ID', 'Well_Depth_BLS'])
# Convert Well_Depth_BLS to numeric with coercion of errors
org_df.loc[:, 'Well_Depth_BLS'] = pd.to_numeric(org_df['Well_Depth_BLS'], errors='coerce')

# Filter wells with depth between 70m and 800m
df = org_df[(org_df['Well_Depth_BLS'] > 70) & (org_df['Well_Depth_BLS'] < 800)].copy()
total_rows = len(df)
print(total_rows)

# Add total_rows text to the bottom-right of the plot
ax.text(0.95, 0.035, f'{total_rows} Wells', transform=ax.transAxes, fontsize=10,
        verticalalignment='bottom', horizontalalignment='right')

# Ensure the data types are correct
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['GWL_Median'] = pd.to_numeric(df['GWL_Median'], errors='coerce')

# Apply the standardization function
df = df.apply(lambda row: standardize_gwl(row), axis=1)

# Drop rows with NaN values
df = df.dropna(subset=['Longitude', 'Latitude', 'GWL_Median'])

lon = df['Longitude'].values
lat = df['Latitude'].values
gwl = df['GWL_Median'].values

# Create grids for kriging
grid_lon = np.linspace(lon.min(), lon.max(), 300)
grid_lat = np.linspace(lat.min(), lat.max(), 300)
grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat)

# Perform Ordinary Kriging
OK = OrdinaryKriging(lon, lat, gwl, 
                     variogram_model='spherical',
                     variogram_parameters={'sill': 1.0, 'range': 0.3, 'nugget': 0.1})

# Perform kriging
z, ss = OK.execute('grid', grid_lon[0, :], grid_lat[:, 0])

# Plotting GWL Contours
levels = np.linspace(-80, 80, 25)
cs = ax.contourf(grid_lon, grid_lat, z, levels=levels, cmap='coolwarm_r', extend='both')
contour_lines = ax.contour(grid_lon, grid_lat, z, levels=[-60, -40, -20], colors='blue', linewidth=0.8)
ax.clabel(contour_lines, inline=True, fontsize=10, fmt='%1.0f m')


# Highlight the -20m, -40m, and -60m contour lines
  #highlighted_contours = ax.contour(grid_lon, grid_lat, z, levels=[-60, -40, -20], colors='blue')

# Calculate the areas enclosed by the contour lines
area_below_60m = calculate_contour_area(contour_lines.collections[0])  # -60m contour
area_below_40m = calculate_contour_area(contour_lines.collections[1])  # -40m contour
area_below_20m = calculate_contour_area(contour_lines.collections[2])  # -20m contour


# Add the area information to the plot (below the legend)
area_text = (f"Areas with GWL below:\n"
             f"-20m: {area_below_20m:.0f} km²\n"
             f"-40m: {area_below_40m:.0f} km²\n"
             f"-60m: {area_below_60m:.0f} km²")

ax.text(0.97, 0.9, area_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right', bbox=dict(facecolor='white', alpha=0.9))

# Set title and labels
ax.set_title(f'{file[-13:-4]} Median GWLs vs. GPS-Derived Subsidence Rates')
counties.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)
ax.plot(loop610['Longitude'], loop610['Latitude'], color='red')

# Define categories and corresponding colors and sizes for subsidence rates
def get_marker_style(subsidence_rate):
    if subsidence_rate <= -20:
        return 'darkred', 320 if subsidence_rate <= -30 else 300
    elif -20 < subsidence_rate <= -15:
        return 'red', 250
    elif -15 < subsidence_rate <= -10:
        return 'yellow', 200
    elif -10 < subsidence_rate <= -5:
        return 'cyan', 150
    elif -5 < subsidence_rate <= 2:
        return 'white', 100
    else:
        return 'gray', 80
        

## Plot Extensometer Sites
#ax.scatter(extensometer_data['Longitude'], extensometer_data['Latitude'], facecolors='none', edgecolors='black', s=300, linewidths=4, label='Extensometers')
# Plot groundwater wells as black dots
ax.scatter(df['Longitude'], df['Latitude'], c='black', s=8, label='Groundwater Wells', zorder=5)  # Wells as small black dots

# Plot GPS data with subsidence rate
for _, row in gps_data.iterrows():
    color, size = get_marker_style(row['Subsidence_Rate'])
    ax.scatter(row['Longitude'], row['Latitude'], c=color, s=size, edgecolors='black', linewidths=0.5, marker='o', label=f'{row["Site_ID"]}: {row["Subsidence_Rate"]} mm/yr')


# Add a custom legend
# Create dummy scatter plots for the legend
gps_marker = plt.scatter([], [], c='white', s=150, edgecolor='black', label='GPS: Color and Size Highlighting Subsidence Rates')
well_marker = plt.scatter([], [], c='black', s=10, label='Groundwater Wells (-70m to -700m)')  # Add well marker for the legend

# Create a Line2D object for the contour legend
# contour_line_legend = Line2D([0], [0], color='blue', linewidth=2, label='Groundwater Level Contours')
contour_line_legend = Line2D([0], [0], color='blue', linewidth=2, linestyle='--', label='GWLs within the Confined Chicot-Evangeline Aquifer')
# Add the legend to the plot
legend = ax.legend(handles=[gps_marker, well_marker, contour_line_legend], loc='upper right', fontsize=10, title="Legend", frameon=True, fancybox=True)

# Set the background of the legend to white
legend.get_frame().set_facecolor('white')


# Create a custom colormap for the color bar
cmap = ListedColormap(['darkred', 'red', 'yellow', 'cyan', 'white', 'gray'])
bounds = [-30, -20, -15, -10, -5, 2, 5]
norm = BoundaryNorm(bounds, cmap.N)

# Add color bar for subsidence rates using the custom colormap
# Add color bar for subsidence rates (slightly above the groundwater colorbar)
cbar_ax_subs = fig.add_axes([0.15, 0.18, 0.4, 0.02])  # GPS Subsidence colorbar positioned above
cbar_subs = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbar_ax_subs, orientation='horizontal')
cbar_subs.set_label('GPS-Derived Subsidence Rate (2020-2024, mm/year)', fontsize=10, backgroundcolor='white', labelpad=10)


# Create a colorbar for groundwater levels
cbar_ax = fig.add_axes([0.17, 0.05, 0.7, 0.02])
fig.colorbar(cs, cax=cbar_ax, orientation='horizontal', label='Contours: Groundwater Levels (m, NAVD88) Within the Confined Chicot-Evangeline Aquifer')

# Set common labels
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

plt.tight_layout()
plt.savefig('GWL_with_Subsidence_and_Extensometers_2020-2024.pdf')
plt.show()

