# viz.py
# Implements shared styling and data visualizations used throughout the project.
import math
import numbers

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# unable to import this from format.py. Why?
def to_percent(rate) -> str:
    """
    Given a rate between 0 and 1, output a user-facing percentage string.

    Examples:
    1.0 -> '100%'
    0.111 -> '11%'
    0.0111 -> '1.1%' 
    """
    if not isinstance(rate, numbers.Real):
        return rate  
    pct = rate * 100
    # output whole percentages after 10% (rounded up)
    if pct >= 9.95:
        return f'{round(pct):,d}%'
    # special case: very small numbers
    if pct == 0:
        return '0%'
    if pct < 0.05:
        return '~0%'
    # single-digit percentages: output one decimal
    return f'{pct:.1f}%'

def set_style():
    """
    Configure default matplotlib styling used throughout the project.
    """
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['savefig.transparent'] = True
    plt.rcParams['savefig.pad_inches'] = 0.1
    plt.rcParams['figure.constrained_layout.use'] = True
    #plt.rcParams['figure.dpi'] = 100
    #plt.rcParams['figure.figsize'] = [6.4, 4.8]
    #plt.rcParams['axes.grid'] = False
    #plt.rcParams['grid.color'] = '#b0b0b0'
    #plt.rcParams['grid.alpha'] = 1.0
    #plt.rcParams['grid.linestyle'] = '-'
    #plt.rcParams['grid.linewidth'] = 0.8

def barh(
    # data
    y,
    width,
    labels = None,
    height = 1,
    left = None,

    # bar styling
    color = None,
    outline_color = 'k',
    outline_width = 0.5,

    # label styling
    label_offset = (4, 0),
    label_offset_coordinates = 'offset points',
    label_fontsize = 11,
    label_fontweight = 'medium',
    label_horizontalalignment = 'left',
    label_vertigalaligment = 'center'
):
    """
    This method closely resembles matplotlib's barh method, but with vastly improved default styling and with the ability to configure labels to annotate each bar.
    """
    bars = plt.barh(y, width, height, left, color = color, edgecolor = outline_color, linewidth = outline_width)
    if labels is not None:
        # could use plt.bar_label, but it does not support as many options as plt.annotate. Most notably, text alignment is missing (!)
        for label, bar, x, _y in zip(labels, bars, width, y):
            plt.annotate(
                label, 
                xy = (x, _y), xytext = label_offset, textcoords = label_offset_coordinates,
                fontsize = label_fontsize, fontweight = label_fontweight,
                verticalalignment = label_vertigalaligment, horizontalalignment = label_horizontalalignment
            )
    return bars

# RATINGS
def rating_to_stars_string(rating) -> str:
    full_stars = math.floor(rating)
    # to do: handle fractional stars (another dataset has them, and they can be the result of aggregates)
    return '★' * full_stars

def plot_ratings(ratings: pd.Series):
    #counts = ratings.value_counts().sort_index(ascending = True)
    counts = ratings.value_counts(normalize = True).sort_index(ascending = True)
    for i in range(1,6):
        if float(i) not in counts.index:
            counts[i] = 0
    #print(counts)
    count = len(ratings)
    y = counts.index.values
    x = counts.values
    weighted_ratings = x * y
    average_rating = weighted_ratings.sum()
    stars_str = f'{average_rating:.1f} ★'
    ratings_str = f'{count} Ratings'
    bars = barh(
        y, x
    )
    max_pct = x.max()
    for bar, pct, _y in zip(bars, x, y):
        label_inside_bar = False
        offset = -4 if label_inside_bar else 4
        text = plt.annotate(
            to_percent(pct),
            xy = (pct, _y),
            xytext = (offset, 0), textcoords = 'offset points',
            verticalalignment = 'center',
            horizontalalignment = 'right' if label_inside_bar else 'left',
            fontsize = 13,
            fontweight = 'bold' if label_inside_bar else 'medium',
            color = 'w' if label_inside_bar else 'k'
        )
    ax = plt.gca()
    ax.set(
        title = f'({ratings_str})',
        yticks = y, yticklabels = map(rating_to_stars_string, y),
        xticks = []
    )
    ax.yaxis.set_tick_params(left = False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.margins(0.2, 0)
    plt.suptitle(f'        {stars_str}', fontsize = 21)

    # enable to debug inspect layout
    #ax.set_facecolor(('k', 0.1))
    #ax.figure.set_facecolor(('k', 0.1))