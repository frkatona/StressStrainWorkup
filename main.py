import zipfile
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from itertools import cycle
from matplotlib.colors import to_rgba


# Function to parse folder names and return sample type
def parse_folder_name(folder_name):
    parts = folder_name.split('_')
    if len(parts) == 3:
        return tuple(parts)
    else:
        return None
    
def read_data(file_path, width_mm, thickness_mm):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    raw_data = []
    for line in lines[8:]:  # Assuming data starts from line 9
        split_line = line.strip().split('\t')
        if len(split_line) >= 4:
            strain = float(split_line[3])
            load = float(split_line[1])
            raw_data.append([strain, load])
    
    # Convert load to stress
    stress_data = calculate_stress(raw_data, width_mm, thickness_mm)

    # Adjust data to start at 0 stress
    first_stress = stress_data[0][1]  # Get the stress value from the first data point
    adjusted_data = [[strain, stress - first_stress] for strain, stress in stress_data]

    return adjusted_data


def calculate_stress(data, width_mm, thickness_mm):
    area = width_mm * thickness_mm  # Area in mm²
    stress_data = []
    for strain, load in data:
        stress = load / area / 1000 # Stress in GPa (assuming load is in N and area in mm²)
        stress_data.append([strain, stress])
    return stress_data


def process_data_folder(data_folder_path):
    sample_data = {}
    for root, dirs, files in os.walk(data_folder_path):
        for file in files:
            if file.endswith('.txt'):
                folder_name = os.path.basename(root)
                sample_type = parse_folder_name(folder_name)
                if sample_type:
                    sample_key = "_".join(sample_type[:2])
                    file_path = os.path.join(root, file)
                    unique_key = f"{sample_key}_{len(sample_data)}"
                    sample_data[unique_key] = file_path

    return sample_data

def fit_and_plot_polynomial(data, degree=3, exclude_final_points=5):
    # Exclude the final 30 points from the fitting process
    if len(data) > exclude_final_points:
        data_for_fit = data[:-exclude_final_points]
    else:
        data_for_fit = data

    x = np.array([point[0] for point in data_for_fit])
    y = np.array([point[1] for point in data_for_fit])
    coefficients = np.polyfit(x, y, degree)
    polynomial = np.poly1d(coefficients)

    # Generate x values for plotting the polynomial fit
    x_fit = np.linspace(x.min(), x.max(), 500)
    y_fit = polynomial(x_fit)

    return x_fit, y_fit

def read_colors(file_path):
    with open(file_path, 'r') as file:
        colors = [line.strip() for line in file.readlines()]
    return colors


def plot_data_with_custom_colors(sample_data, colors_file_path, width_mm, thickness_mm):
    custom_colors = read_colors(colors_file_path)
    color_iterator = cycle(custom_colors)

    color_mapping = {}
    for key in sample_data.keys():
        x_y_prefix = "_".join(key.split('_')[:2])
        if x_y_prefix not in color_mapping:
            color_mapping[x_y_prefix] = next(color_iterator)

    plt.figure(figsize=(12, 8))

    added_to_legend = set()
    for sample_key, file_path in sample_data.items():
        x_y_prefix = "_".join(sample_key.split('_')[:2])
        base_color = color_mapping[x_y_prefix]
        color_rgba = to_rgba(base_color)
        reduced_saturation_color = (color_rgba[0], color_rgba[1], color_rgba[2], 0.25)

        data = read_data(file_path, width_mm, thickness_mm)
        df = pd.DataFrame(data, columns=['Strain (mm/mm)', 'Stress (GPa)'])

        plt.plot(df['Strain (mm/mm)'], df['Stress (GPa)'], color=reduced_saturation_color)
        
        # Fit and plot polynomial with full color
        x_fit, y_fit = fit_and_plot_polynomial(data, degree=3)
        if x_y_prefix not in added_to_legend:
            plt.plot(x_fit, y_fit, color=base_color, label=x_y_prefix)
            added_to_legend.add(x_y_prefix)
        else:
            plt.plot(x_fit, y_fit, color=base_color)

    plt.xlabel('Strain (mm/mm)')
    plt.ylabel('Stress (GPa)')
    plt.title('Stress-Strain for Paper-PDMS Samples with 3rd-order Polynomial Fit')
    plt.legend()
    plt.grid(True)
    plt.show()

## Define the dimensions of the sample (in mm)
width_mm = 0.1
thickness_mm = 0.01

## process and plot data
data_folder_path = r"CSVs\24-01-08_Tensile_paper-PDMS"
colors_folder_path = "dist\colorlist_lear.txt"
sample_data = sample_data = process_data_folder(data_folder_path)
plot_data_with_custom_colors(sample_data, colors_folder_path, width_mm, thickness_mm)