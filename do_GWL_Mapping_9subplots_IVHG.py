#!/usr/bin/python3
## 5-15-2024, plots 9 subplot each page

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from pykrige.ok import OrdinaryKriging
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.cm as cm  # Function to calculate the area within a contour
from matplotlib.path import Path
from shapely.geometry import Polygon
import matplotlib.ticker as ticker

# List of files with data for different periods
files = [
    'Houston_Wells_LL_GWL_1920-1940.lld',
    'Houston_Wells_LL_GWL_1940-1944.lld',
    'Houston_Wells_LL_GWL_1950-1954.lld',
    'Houston_Wells_LL_GWL_1960-1964.lld',
    'Houston_Wells_LL_GWL_1970-1974.lld',
    'Houston_Wells_LL_GWL_1980-1984.lld',
    'Houston_Wells_LL_GWL_1990-1994.lld',
    'Houston_Wells_LL_GWL_2000-2004.lld',
    'Houston_Wells_LL_GWL_2010-2014.lld'  
]


# Read county shape data and prepare Loop 610 data
counties = gpd.read_file('County.shp').to_crs("EPSG:4326")
loop610 = pd.read_csv('Houston_IH610_inner_loop.psxy', delimiter=' ', header=0)

## Well_Depth_BLS is positive numbers
def standardize_gwl(row, ivhg=-0.07, target_depth=300):
    # Calculate depth difference
    depth_diff = target_depth - row['Well_Depth_BLS']
    # Adjust GWL_Median based on IVHG and depth difference
    row['GWL_Median'] = round(row['GWL_Median'] + depth_diff * ivhg, 1)
    return row
    
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
fig, axs = plt.subplots(3, 3, figsize=(10, 12.8), sharex=True, sharey=True)

# Loop through each axis in the array to set the same x and y limits
for ax_row in axs:
    for ax in ax_row:
        ax.set_xlim([-95.95, -94.7])
        ax.set_ylim([29.1, 30.4])
        ax.xaxis.set_major_locator(ticker.MaxNLocator(prune='both', nbins=4))
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))

for ax, file in zip(axs.flatten(), files):
    # Load data from the current file
    org_df = pd.read_csv(file, delimiter='\t', names=['Longitude', 'Latitude', 'GWL_Median', 'Well_ID', 'Well_Depth_BLS'])
    # Ensure the data types are correct before filtering to avoid issues in conditional checks
    org_df['Well_Depth_BLS'] = pd.to_numeric(org_df['Well_Depth_BLS'], errors='coerce')
    
    # Load the data, filtering out wells with depth less than  70m or deeper than 800m
    df = org_df[(org_df['Well_Depth_BLS'] > 70) & (org_df['Well_Depth_BLS'] < 800)]
    total_rows = len(df)
    print (total_rows)
        
    # Add total_rows text to the bottom-right of each subplot
    ax.text(0.95, 0.035, f'{total_rows} Wells', transform=ax.transAxes, fontsize=8,
            verticalalignment='bottom', horizontalalignment='right', bbox=dict(facecolor='white', alpha=0.8))
            
    
        
    # Ensure the data types are correct
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['GWL_Median'] = pd.to_numeric(df['GWL_Median'], errors='coerce')
    df['Well_Depth_BLS'] = pd.to_numeric(df['Well_Depth_BLS'], errors='coerce')
    
    # Print the first 10 rows before standardization
    print("Before Standardization:")
    print(df[['GWL_Median', 'Well_Depth_BLS']].head(10))

    
    # Apply the standardization function
    df = df.apply(lambda row: standardize_gwl(row), axis=1)
    
    # Print the first 10 rows after standardization
    print("After Standardization:")
    print(df[['GWL_Median', 'Well_Depth_BLS']].head(10))   
    
    
    # Drop rows with NaN values that may result from conversion errors
    df = df.dropna(subset=['Longitude', 'Latitude', 'GWL_Median'])

    lon = df['Longitude'].values
    lat = df['Latitude'].values
    gwl = df['GWL_Median'].values

    # Create grids for kriging
    grid_lon = np.linspace(lon.min(), lon.max(), 300)
    grid_lat = np.linspace(lat.min(), lat.max(), 300)
    grid_lon, grid_lat = np.meshgrid(grid_lon, grid_lat)

    ## Perform Ordinary Kriging
    #OK = OrdinaryKriging(lon, lat, gwl, variogram_model='spherical')
    #z, _ = OK.execute('grid', grid_lon[0,:], grid_lat[:,0])
    
    # Example using the complex model
    OK = OrdinaryKriging(
    lon, lat, gwl, 
    variogram_model='spherical',
    variogram_parameters={'sill': 1.0, 'range': 0.3, 'nugget': 0.1}
    )
    ## note the unit of range is degree
    
    # Perform kriging
    z, ss = OK.execute('grid', grid_lon[0,:], grid_lat[:,0])
    
    # Plotting
    levels = np.linspace(-80, 80, 25)
    cs = ax.contourf(grid_lon, grid_lat, z, levels=levels, cmap='coolwarm_r', extend='both')
    ax.scatter(lon, lat, marker='o', c='gray', s=6, edgecolors='gray', linewidths=0.2)
    contour_lines = ax.contour(grid_lon, grid_lat, z, levels=[-60, -40, -20], colors='blue', linewidth=0.6)
    ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%1.0f m')

    # Set titles and labels
    ax.set_title(f'{file[-13:-4]} Median GWLs')
    counties.plot(ax=ax, color='none', edgecolor='black', linewidth=0.5)
    ax.plot(loop610['Longitude'], loop610['Latitude'], color='red')
    
    # calculate and mark areas at -20m, -40m, and -60m
    # Highlight the -20m, -40m, and -60m contour lines
      #highlighted_contours = ax.contour(grid_lon, grid_lat, z, levels=[-60, -40, -20], colors='blue')
      #contour_lines = ax.contour(grid_lon, grid_lat, z, levels=[-60, -40, -20], colors='blue', linewidth=0.7)
    # Calculate the areas enclosed by the contour lines
    area_below_60m = calculate_contour_area(contour_lines.collections[0])  # -60m contour
    area_below_40m = calculate_contour_area(contour_lines.collections[1])  # -40m contour
    area_below_20m = calculate_contour_area(contour_lines.collections[2])  # -20m contour


# Add the area information to the plot (below the legend)
    area_text = (f"Areas below:\n"
             f"-20m: {area_below_20m:.0f} km²\n"
             f"-40m: {area_below_40m:.0f} km²\n"
             f"-60m: {area_below_60m:.0f} km²")

    ax.text(0.45, 0.2, area_text, transform=ax.transAxes, fontsize=8,
        verticalalignment='top', horizontalalignment='right', bbox=dict(facecolor='white', alpha=0.8))


# Adjust subplots
plt.subplots_adjust(bottom=0.12, hspace=0.2)  # Adjust the bottom margin and the vertical spacing

# Create a colorbar
cbar_ax = fig.add_axes([0.17, 0.05, 0.7, 0.02])
fig.colorbar(cs, cax=cbar_ax, orientation='horizontal', label='Hydraulic Head (M, NAVD88) in the Chicot-Evangeline Aquifer at -300 m')

# Set common labels
for ax in axs[2, :]:
    ax.set_xlabel('Longitude')
for ax in axs[:, 0]:
    ax.set_ylabel('Latitude')

#plt.tight_layout()
#plt.tight_layout(pad=0.0, h_pad=0.1, w_pad=0.1)  # Adjusted padding and horizontal/vertical padding

plt.savefig('GWL_IVHG_9subplots.pdf')
plt.show()

