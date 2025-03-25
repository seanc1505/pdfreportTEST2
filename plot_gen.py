import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def save_plot(data, plot_type, xlabel, ylabel, title, filename, facecolor=(247/256, 240/256, 231/256)):
    """
    Generate and save a plot (bar or line) based on input parameters.
    
    Parameters:
    - data (pd.DataFrame): Data to plot
    - plot_type (str): 'bar' or 'line'
    - xlabel (str): Label for x-axis
    - ylabel (str): Label for y-axis
    - title (str): Plot title
    - filename (str): File path to save the plot
    - facecolor (tuple): Background color
    """
    fig, ax = plt.subplots(facecolor=facecolor)
    
    # Define larger font sizes
    title_size = 18
    label_size = 12
    tick_size = 18
    # Automatically wrap Y-label if it's too long
    max_label_length = 15  # Set threshold for breaking
    if len(ylabel) > max_label_length:
        split_index = ylabel[:max_label_length].rfind(" ")  # Find last space before threshold
        if split_index == -1: 
            split_index = max_label_length  # If no space, break at max length
        ylabel = ylabel[:split_index] + "\n" + ylabel[split_index+1:]

    if plot_type == 'bar':
        colors = ['#FF6F61', '#6B5B95']  # First = Red/Orange, Second = Purple
        bar_width = 0.5  # Width of bars
        x = np.arange(len(data))  # X positions for bars (each row)

        # Plot individual bars for each row
        for i, (index, row) in enumerate(data.iterrows()):
            bars = ax.bar(i, row.iloc[0], color=colors[i], width=bar_width, label=index)
            for bar in bars:
                height = bar.get_height()
                if height > 0:  # Only show if value > 0
                    ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}', 
                            ha='center', va='bottom', fontsize=26)

    
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(data.index, rotation=0, fontsize=tick_size)  # Increase tick label size
    elif plot_type == 'line':
        data.plot(
    kind='line',
    ax=ax,
    style='s',
    linestyle=(0, (6,2)),             # square markers + dashed line
    markersize=8,               # smaller markers
    linewidth=1,              # thinner line
    figsize=(8, 4),
    grid=False,
    color='#6B5B95'
)
        # Change X-axis to numeric positions
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(data.index, rotation=45)  # Rotate for better readability
        ax.legend().remove()
        # Add value labels next to each point only if greater than 0
        for i, txt in enumerate(data.iloc[:, 0]):
            if txt > 0:  # Only show if value > 0
                ax.annotate(f'{txt:.1f}', (i, data.iloc[i, 0]), textcoords="offset points",
                            xytext=(0, 15), ha='center', fontsize=12, fontweight='normal', color='black')

    else:
        raise ValueError("Unsupported plot type. Use 'bar' or 'line'.")
    min_value = data.min().min()  # Get the lowest y-value
    max_value = data.max().max()
    buffer = max_value * 0.15
    ax.set_ylim(min_value-buffer, max_value + buffer)
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))  # Limits number of Y-ticks to ~5
    ax.tick_params(axis='y', labelsize=tick_size)  # Make Y-axis labels larger
    ax.set_xlabel(xlabel, fontsize=label_size)
    ax.set_ylabel(ylabel, fontsize=label_size,rotation=0, labelpad=80)
    ax.set_title(title, fontsize=title_size)
    ax.set_facecolor(facecolor)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.5)  # Ensures text is fully visible
    plt.close(fig)


def plot_bar_multiple(data_list, labels, ylabel, title, filename):
    """Generate a multi-subplot bar chart and save it with larger font sizes."""
    num_plots = len(data_list)
    fig, axes = plt.subplots(num_plots, 1, layout="constrained", facecolor=(247/256, 240/256, 231/256), figsize=(8, num_plots * 3))

    # Define larger font sizes
    title_size = 24
    label_size = 22
    tick_size = 12
    # Automatically wrap Y-label if it's too long
    max_label_length = 10  # Set threshold for breaking
    if len(ylabel) > max_label_length:
        split_index = ylabel[:max_label_length].rfind(" ")  # Find last space before threshold
        if split_index == -1: 
            split_index = max_label_length  # If no space, break at max length
        ylabel = ylabel[:split_index] + "\n" + ylabel[split_index+1:]
    if num_plots == 1:
        axes = [axes]  # Ensure it's iterable if there's only one subplot

    for ax, (data, label) in zip(axes, zip(data_list, labels)):
        bars = ax.bar(range(len(data)), data, color='#FF6F61')  # Match requested style
        max_height = max(data)
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=12)
        
        buffer = max_height * 0.15
        ax.set_ylim(0, max_height + buffer)
        ax.yaxis.set_major_locator(plt.MaxNLocator(5))  # Limits number of Y-ticks to ~5
        ax.tick_params(axis='y', labelsize=tick_size)  # Make Y-axis labels larger
        ax.bar(range(len(data)), data, color='#FF6F61')  # Match requested style
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(range(24), fontsize=tick_size)
        ax.set_ylabel(ylabel, fontsize=label_size,rotation=0, labelpad=80)
        ax.set_title(label, fontsize=title_size)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_facecolor((247/256, 240/256, 231/256))

    fig.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.5)  # Ensures text is fully visible
    plt.close(fig)
