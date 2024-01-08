import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load the data from the CSV file
df = pd.read_csv('CSVs/pre-processed.csv')

# Create a color palette with a different color for each 'Sample Type'
palette = sns.husl_palette(df['Sample Type'].nunique(), s=.5)

# Create a figure and axis for the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Use seaborn to create a scatter plot with different colors for each 'Sample ID'
scatter = sns.scatterplot(x='mm/mm', y='Stress', hue='Sample Type', style='Sample ID', data=df, palette=palette, ax=ax)

# Calculate and plot a linear regression line for each 'Sample ID' in the filtered data
handles, labels = ax.get_legend_handles_labels()
slopes = []

for sample_id in df['Sample ID'].unique():
    df_sample = df[df['Sample ID'] == sample_id]
    slope, intercept, r_value, p_value, std_err = stats.linregress(df_sample['mm/mm'], df_sample['Stress'])
    x = df_sample['mm/mm']
    y = slope * x + intercept
    color = scatter.get_legend().legendHandles[labels.index(sample_id.split('_')[0])].get_facecolor()
    ax.plot(x, y, color=color)
    slopes.append((sample_id.split('_')[0], slope))  # Save the 'Sample Type' and slope

# Set the plot title and labels
ax.set_title('Stress vs Strain with Linear Regression Lines')
ax.set_xlabel('Strain (mm/mm)')
ax.set_ylabel('Stress (MPa)')

# Show the plot
plt.show()

# Convert the list of slopes into a DataFrame
df_slopes = pd.DataFrame(slopes, columns=['Sample Type', 'Slope'])

# Calculate the mean and standard deviation of the slopes for each 'Sample Type'
df_slopes_summary = df_slopes.groupby('Sample Type').agg(['mean', 'std']).reset_index()

# Create a bar graph of the average slopes with error bars
plt.figure(figsize=(10, 6))
plt.bar(df_slopes_summary['Sample Type'], df_slopes_summary['Slope']['mean'], 
        yerr=df_slopes_summary['Slope']['std'], capsize=10, color=palette)
plt.title('Average Modulus for Each Sample Type')
plt.xlabel('Sample Type')
plt.ylabel('Modulus (MPa)')
plt.show()

# Print the slopes
print(df_slopes)