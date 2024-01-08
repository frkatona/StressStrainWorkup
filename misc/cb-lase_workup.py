import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress
from scipy.ndimage import gaussian_filter1d
from skimage.io import imread

def linear_func(x, a, b):
    return a * x + b

# Define the path to your folder
path = "path_to_your_folder"

# Define a colormap for "oven" and "speedmax" samples
cmap_speedmax = plt.get_cmap("viridis")
oven_color = "salmon"

# Initialize empty lists to store dataframes and file names
dfs = []
file_names = []

# Walk through the directory
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.txt'):
            # Read the text file into a dataframe
            df = pd.read_csv(os.path.join(root, file), sep='\t', skiprows=5)
            
            # Calculate the stress
            df["Stress (MPa)"] = df["Load  "] / 40
            
            # Store the dataframe and the file name
            dfs.append(df)
            file_names.append(os.path.basename(root)[15:])

# Sort the dataframes and file names by the file names
dfs, file_names = zip(*sorted(zip(dfs, file_names), key=lambda x: x[1]))

# Create a figure and an axes for stress-strain curves
fig1, ax1 = plt.subplots(figsize=(10, 8))

# Reset the counters
speedmax_counter = 0

# Plot the stress-strain curves for each dataframe with baseline correction, fitting and smoothing
for i, df in enumerate(dfs):
    # Select the data between 0 and 0.2 strain
    df_fit = df[(df["Strain 1"] >= 0) & (df["Strain 1"] <= 0.2)]
    
    # Fit a line to the data
    slope, intercept, r_value, p_value, std_err = linregress(df_fit["Strain 1"], df_fit["Adjusted Stress (MPa)"])
    
    # Smooth the data using a Gaussian filter
    smoothed_stress = gaussian_filter1d(df["Adjusted Stress (MPa)"], sigma=2)
    
    # Choose the colormap and update the corresponding counter based on the sample type
    if "oven" in file_names[i]:
        color = oven_color
    else:
        color = cmap_speedmax(speedmax_counter / num_speedmax)
        speedmax_counter += 1

    # Plot the smoothed data
    ax1.plot(df["Strain 1"], smoothed_stress, color=color, label=file_names[i])
    
    # Plot the fitted line between 0 and 0.2 strain
    x_fit = np.linspace(0, 0.2, 100)
    y_fit = slope * x_fit + intercept
    ax1.plot(x_fit, y_fit, color=color, linestyle='--', linewidth=4.0)

# Set the labels and the title for the stress-strain curves
ax1.set_xlabel("Strain (mm/mm)")
ax1.set_ylabel("Adjusted Stress (MPa)")
ax1.set_title("5ppt cbPDMS under oven (200C) or lase (15W, 1D, 3000mm/min tri.) conditions")

# Add a legend
ax1.legend()

# Show the plot
plt.show()

# Create a figure and an axes for the bar graph
fig2, ax2 = plt.subplots(figsize=(10, 8))

# Reset the counters
speedmax_counter = 0

# Define the new labels for speedmax samples
speedmax_labels = ["3min", "4min", "5min", "6min", "7min", "8min"]

# Plot the bar graph
ax2.bar("oven", oven_slope_mean, yerr=oven_slope_std, capsize=10, color=oven_color)

for i, slope in enumerate(speedmax_slopes):
    color = cmap_speedmax(i / len(speedmax_slopes))
    ax2.bar(speedmax_labels[i], slope, color=color)

# Set the labels for the bar graph
ax2.set_xlabel("Sample")
ax2.set_ylabel("Young's Modulus")

# Show the plot
plt.show()