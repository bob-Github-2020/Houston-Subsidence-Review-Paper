#!/usr/bin/python3

import pandas as pd
import matplotlib.pyplot as plt

# Load the data
data = pd.read_csv('HGSD_GW_by_Use.csv')

# Define the columns for the different uses
years = data['Year']
total_use = data['Total']
public_use = data['Public']
industrial_use = data['Industrial']
irrigation_use = data['AllIrrigation']

# Create the figure and axis for the bar chart
fig, ax = plt.subplots(figsize=(11, 8))

# Plot the data in a stacked bar chart
ax.bar(years, public_use, label='Public Use', color='steelblue')
ax.bar(years, industrial_use, bottom=public_use, label='Industrial Use', color='orange')
ax.bar(years, irrigation_use, bottom=public_use + industrial_use, label='Irrigation Use', color='green')

# Set the title and labels
ax.set_title('Groundwater Use in Harris and Galveston Counties (1976 - 2023)', fontsize=12)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Groundwater Use (MGD)', fontsize=12)

# Set x-ticks to show every 2 years
ax.set_xticks(years[::2])  # This selects every 2nd year

# Set Y-axis range from 0 to 550
ax.set_ylim(0, 600)

# Add a legend
ax.legend(loc=(0.05, 0.85))

# Rotate the x-axis labels for better readability
plt.xticks(rotation=45)

# Tight layout to ensure labels and title fit well
plt.tight_layout()

# Get the total groundwater use for 1976 and 2023
total_1976 = data.loc[data['Year'] == 1976, 'Total'].values[0]
total_2023 = data.loc[data['Year'] == 2023, 'Total'].values[0]
total_2011 = data.loc[data['Year'] == 2011, 'Total'].values[0]

# Add two pie charts in the top-right area of the figure
# For 1976
ax1 = fig.add_axes([0.3, 0.62, 0.2, 0.3])  # Adjust position of pie chart
use_1976 = data.loc[data['Year'] == 1976, ['Public', 'Industrial', 'AllIrrigation']].values[0]
labels = ['Public', 'Industrial', 'Irrigation']
ax1.pie(use_1976, labels=labels, autopct='%1.1f%%', colors=['steelblue', 'orange', 'green'])
ax1.set_title(f'1976 GW Use: {total_1976:.1f} MGD', fontsize=11)  # Include total use in title

# For 2011
ax1 = fig.add_axes([0.51, 0.62, 0.2, 0.3])  # Adjust position of pie chart
use_2011 = data.loc[data['Year'] == 2011, ['Public', 'Industrial', 'AllIrrigation']].values[0]
labels = [' ', ' ', ' ']
ax1.pie(use_2011, labels=labels, autopct='%1.1f%%', colors=['steelblue', 'orange', 'green'])
ax1.set_title(f'2011 GW Use: {total_2011:.1f} MGD', fontsize=11)  # Include total use in title

# For 2023
ax2 = fig.add_axes([0.72, 0.62, 0.2, 0.3])  # Adjust position of pie chart
use_2023 = data.loc[data['Year'] == 2023, ['Public', 'Industrial', 'AllIrrigation']].values[0]
labels = ['Public', 'Industrial', 'Irrigation']
ax2.pie(use_2023, labels=labels, autopct='%1.1f%%', colors=['steelblue', 'orange', 'green'])
ax2.set_title(f'2023 GW Use: {total_2023:.1f} MGD', fontsize=11)  # Include total use in title

# Save the plot as a PNG file
plt.savefig('HGSD_GW_by_use_Histogram.png', dpi=300)

# Save the plot as a high-resolution PDF file
plt.savefig('HGSD_GW_by_use_Histogram.pdf', format='pdf', dpi=350)

# Show the plot
plt.show()


