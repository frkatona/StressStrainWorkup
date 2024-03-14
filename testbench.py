import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from numpy.polynomial.polynomial import Polynomial
from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy import stats

def process_directory_and_plot(directory_path):
    slopes = []
    group_labels = []  # Labels for groups for Tukey's HSD

    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        # Load the data
        data = pd.read_csv(file_path, sep="\t", skiprows=9, usecols=[1, 3], header=None, names=["Load", "Strain"])
        
        # Filtering for the linear fit between 0.05 and 0.2 strain
        linear_data = data[(data['Strain'] >= 0.05) & (data['Strain'] <= 0.2)]
        linear_p = Polynomial.fit(linear_data['Strain'], linear_data['Load'], 1)
        
        # Adjust the slope by dividing by 6 and store it with group label
        adjusted_slope = linear_p.convert().coef[1] / 6
        slopes.append(adjusted_slope)
        if 'laser-' in file:
            group_labels.append('Laser-Oven')
        elif 'oven-laser' in file:
            group_labels.append('Oven-Laser')
        elif 'laser_' in file:
            group_labels.append('Laser')
        elif 'oven_' in file:
            group_labels.append('Oven')

    # ANOVA to test for overall significance
    f_stat, p_value_anova = f_oneway(*[np.array(slopes)[np.array(group_labels) == group] for group in set(group_labels)])
    print(f"ANOVA F-statistic: {f_stat:.4f}, p-value: {p_value_anova:.4f}")

    # Tukey's HSD test for pairwise comparisons
    tukey = pairwise_tukeyhsd(endog=slopes, groups=group_labels, alpha=0.05)
    print(tukey)

    # Group means and standard deviations for plotting
    # groups = sorted(set(group_labels))
    groups = ['Oven', 'Oven-Laser', 'Laser', 'Laser-Oven']
    means = [np.mean(np.array(slopes)[np.array(group_labels) == group]) for group in groups]
    errors = [np.std(np.array(slopes)[np.array(group_labels) == group]) for group in groups]

    # Perform t-test on last two means
    t_stat, p_value_ttest = stats.ttest_ind(means[-2:], errors[-2:])
    print(f"T-test: t-statistic: {t_stat:.4f}, p-value: {p_value_ttest:.4f}")

    # Plotting
    plt.figure(figsize=(10, 6))
    colors = ['#ff7440', '#aba000', '#7840a1', '#b34256']
    plt.bar(groups, means, yerr=errors, capsize=5, color=colors)
    plt.ylabel('youngs modulus /MPa')
    plt.grid(False)
    plt.show()

# Main
directory_path = 'CSVs\oven-laser_combinations'
process_directory_and_plot(directory_path)