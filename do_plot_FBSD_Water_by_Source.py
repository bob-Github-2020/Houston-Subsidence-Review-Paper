#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt

# Load the data
data = pd.read_csv('FBSD_GW_by_Source.csv')

# Define the columns for the different uses
years = data['Year']
total_use = data['Total']
groundwater_use = data['Groundwater']
#trinity_use = data['San Jacinto/Trinity']
san_jacinto_use = data['San Jacinto']
brazos_use = data['Brazos']
reclaimed_use = data['Reclaimed']

# Create the figure and axis for the bar chart
fig, ax = plt.subplots(figsize=(11, 8))

# Plot the data in a stacked bar chart
ax.bar(years, groundwater_use, label='Groundwater', color='steelblue')
#ax.bar(years, trinity_use, bottom=groundwater_use, label='Trinity', color='orange')
ax.bar(years, san_jacinto_use, bottom=groundwater_use, label='San Jacinto/Trinity', color='green')
ax.bar(years, brazos_use, bottom=groundwater_use + san_jacinto_use, label='Brazos', color='purple')
ax.bar(years, reclaimed_use, bottom=groundwater_use + san_jacinto_use + brazos_use, label='Reclaimed', color='yellow')

# Set the title and labels
ax.set_title('Total Water Use in Fort Bend County (1990 - 2023)', fontsize=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Total Water Use (MGD)', fontsize=12)

# Set x-ticks to show every 2 years
ax.set_xticks(years[::2])  # This selects every 2nd year

# Set Y-axis range from 0 to 900 (adjust as needed based on the range of your data)
ax.set_ylim(0, 350)

# Add a legend
ax.legend(loc=(0.05, 0.85))

# Rotate the x-axis labels for better readability
plt.xticks(rotation=45)

# Tight layout to ensure labels and title fit well
plt.tight_layout()

# Get the total water use for 1976 and 2023
total_1990 = data.loc[data['Year'] == 1990, 'Total'].values[0]
total_2023 = data.loc[data['Year'] == 2023, 'Total'].values[0]
total_2011 = data.loc[data['Year'] == 2011, 'Total'].values[0]

# Add two pie charts in the top-right area of the figure
# For 1990
ax1 = fig.add_axes([0.3, 0.62, 0.2, 0.3])  # Adjust position of pie chart
use_1990 = data.loc[data['Year'] == 1990, ['Groundwater', 'San Jacinto', 'Brazos', 'Reclaimed']].values[0]
labels = ['Groundwater', 'ST', 'Brazos', ' ']
ax1.pie(use_1990, labels=labels, autopct='%1.1f%%', colors=['steelblue', 'green', 'purple', 'yellow'])
ax1.set_title(f'1990 Total Use: {total_1990:.1f} MGD', fontsize=11)  # Include total use in title

# For 2011
ax1 = fig.add_axes([0.51, 0.62, 0.2, 0.3])  # Adjust position of pie chart
use_2011 = data.loc[data['Year'] == 2011, ['Groundwater', 'San Jacinto', 'Brazos', 'Reclaimed']].values[0]
labels = ['Groundwater', 'ST', 'Brazos', ' ']
ax1.pie(use_2011, labels=labels, autopct='%1.1f%%', colors=['steelblue', 'green', 'purple', 'yellow'])
ax1.set_title(f'2011 Total Use: {total_2011:.1f} MGD', fontsize=11)  # Include total use in title

# For 2023
ax2 = fig.add_axes([0.72, 0.62, 0.2, 0.3])  # Adjust position of pie chart
use_2023 = data.loc[data['Year'] == 2023, ['Groundwater',  'San Jacinto', 'Brazos', 'Reclaimed']].values[0]
labels = ['Groundwater', 'ST', 'Brazos', 'Reclaimed']
ax2.pie(use_2023, labels=labels, autopct='%1.1f%%', colors=['steelblue', 'green', 'purple', 'yellow'])
ax2.set_title(f'2023 Total Use: {total_2023:.1f} MGD', fontsize=11)  # Include total use in title

# Save the plot as a PNG file
plt.savefig('FBSD_Total_Water_Use_Histogram.png', dpi=300)

# Save the plot as a high-resolution PDF file
plt.savefig('FBSD_Total_Water_Use_Histogram.pdf', format='pdf', dpi=350)

# Show the plot
plt.show()

