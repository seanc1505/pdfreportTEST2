import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def save_plot(
    data,
    plot_type,
    xlabel,
    ylabel,
    title,
    filename,
    facecolor=(247/256, 240/256, 231/256)
):
    """
    Generate and save a plot (bar or line) based on input parameters.

    Parameters
    ----------
    data : pd.DataFrame
        Data to plot (assumes one column of data).
        The DataFrame must be indexed by its x-values.
    plot_type : str
        Either 'bar' or 'line'.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis (auto-wraps if too long).
    title : str
        Plot title.
    filename : str
        File path to save the resulting plot.
    facecolor : tuple
        Background color as an (R, G, B) tuple with floats in [0,1].
    """

    fig, ax = plt.subplots(facecolor=facecolor)

    # Larger font sizes
    title_size = 18
    label_size = 16
    tick_size = 16

    # Auto-wrap y-label if it's too long
    max_label_length = 15
    if len(ylabel) > max_label_length:
        split_index = ylabel[:max_label_length].rfind(" ")
        if split_index == -1:
            split_index = max_label_length
        ylabel = ylabel[:split_index] + "\n" + ylabel[split_index+1:]

    if plot_type == 'bar':
        # Simple 2-color palette
        colors = ['#FF6F61', '#6B5B95']
        bar_width = 0.5

        # Use np.arange to space out the bars
        x_positions = np.arange(len(data))

        # Plot each row as an individual bar
        for i, (idx, row) in enumerate(data.iterrows()):
            bar_value = row.iloc[0]
            bars = ax.bar(
                x_positions[i],
                bar_value,
                color=colors[i % len(colors)],
                width=bar_width,
                label=str(idx)
            )
            # Annotate if > 0
            if bar_value > 0:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        height,
                        f'{height:.1f}',
                        ha='center',
                        va='bottom',
                        fontsize=16
                    )

        ax.set_xticks(x_positions)
        ax.set_xticklabels(data.index, rotation=0, fontsize=tick_size)

    elif plot_type == 'line':
        # Plot each row in 'data' (but typically you have 1 column)
        # NOTE: key difference from your original approach is we use data.index
        # as the X-values, not 0..N. This keeps points & labels aligned.
        ax.plot(
            data.index,
            data.iloc[:, 0],
            marker='s',
            linestyle=(0, (6, 2)),  # dashed pattern
            markersize=8,
            linewidth=1,
            color='#6B5B95'
        )

        # Annotate each data point
        for x_val, y_val in data.iloc[:, 0].items():
            if y_val > 0:
                ax.annotate(
                    f'{y_val:.1f}',
                    (x_val, y_val),
                    xytext=(0, 8),
                    textcoords='offset points',
                    ha='center',
                    fontsize=12
                )

        # Ensure tick labels match the actual index
        ax.set_xticks(data.index)
        ax.set_xticklabels(data.index, rotation=0)

        # If a Pandas legend is auto-generated, remove it:
        if ax.get_legend():
            ax.legend().remove()
    else:
        raise ValueError("Unsupported plot type. Use 'bar' or 'line'.")

    # Adjust Y-limits to have a bit of space above
    min_value = data.min().min()
    max_value = data.max().max()
    buffer = (max_value - min_value) * 0.15 if (max_value - min_value) != 0 else 0.05
    ax.set_ylim(min_value - buffer, max_value + buffer)

    # Limit Y-axis ticks to ~5
    ax.yaxis.set_major_locator(plt.MaxNLocator(5))

    ax.tick_params(axis='both', labelsize=tick_size)

    # Labels & title
    ax.set_xlabel(xlabel, fontsize=label_size)
    ax.set_ylabel(ylabel, fontsize=label_size, rotation=0, labelpad=80)
    ax.set_title(title, fontsize=title_size)

    # Style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.savefig(
        filename,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.5
    )
    plt.close(fig)


def plot_bar_multiple(
    data_list, 
    labels, 
    ylabel, 
    title, 
    filename
):
    """
    Generate a multi-subplot bar chart and save it with larger font sizes.

    Parameters
    ----------
    data_list : list of list-like
        Each element is a list/array of numeric values to plot in a bar chart.
    labels : list of str
        Titles for each subplot in the same order as data_list.
    ylabel : str
        Label for the y-axis (auto-wrap if long).
    title : str
        Overall figure title or repeated subplot title.
    filename : str
        File path to save the resulting chart image.
    """
    num_plots = len(data_list)

    fig, axes = plt.subplots(
        num_plots,
        1,
        layout="constrained",
        facecolor=(247/256, 240/256, 231/256),
        figsize=(8, num_plots * 3)
    )

    title_size = 24
    label_size = 22
    tick_size = 12

    max_label_length = 10
    if len(ylabel) > max_label_length:
        split_index = ylabel[:max_label_length].rfind(" ")
        if split_index == -1:
            split_index = max_label_length
        ylabel = ylabel[:split_index] + "\n" + ylabel[split_index+1:]

    if num_plots == 1:
        axes = [axes]

    for ax, (data_values, subplot_title) in zip(axes, zip(data_list, labels)):
        bars = ax.bar(range(len(data_values)), data_values, color='#FF6F61')
        max_height = max(data_values) if len(data_values) else 1

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f'{height:.1f}',
                    ha='center',
                    va='bottom',
                    fontsize=12
                )

        buffer = max_height * 0.15
        ax.set_ylim(0, max_height + buffer)

        ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        ax.tick_params(axis='y', labelsize=tick_size)

        ax.set_xticks(range(len(data_values)))
        ax.set_xticklabels(range(len(data_values)), fontsize=tick_size)

        ax.set_ylabel(ylabel, fontsize=label_size, rotation=0, labelpad=80)
        ax.set_title(subplot_title, fontsize=title_size)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_facecolor((247/256, 240/256, 231/256))

    fig.savefig(
        filename,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.5
    )
    plt.close(fig)
