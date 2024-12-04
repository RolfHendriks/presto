# viz.py
# Implements shared styling and data visualizations used throughout the project.
import math
import numbers

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.artist import Artist
from matplotlib.text import Text
from matplotlib.axes import Axes
import matplotlib.patheffects as path_effects

import pandas as pd

############
# Utils
###########

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

# Add outline to text (or any other element)
def add_outline(artist: mpl.artist.Artist, color = 'k', linewidth = 1):
    artist.set_path_effects([
        path_effects.Stroke(linewidth=linewidth, foreground=color),
        path_effects.Normal()
    ])

def plot_rates(
    y, width,
    color = None, edgecolor = 'k',
    label_inside_bar_cutoff = 0.75,
    barheight = 0.9, bgbarheight = 0.8, bgbarcolor = ('k', 0.05),
    labeloffset = 8, labelfontsize = 13, 
    show_x_axis = True,
    ax: Axes = None
):
    """
    Given a list of rates from 0-1, outputs a custom bar graph optimized for displaying percentages.
    """
    ax = ax or plt.gca()
    ticks = [0, 20, 40, 60, 80, 100]
    percents = [x * 100 for x in width]
    bars = ax.barh(y, percents, height = barheight, edgecolor = edgecolor, linewidth = 0.5, color = color)
    bgbars = ax.barh(y, [100 - x - 1 for x in percents], left = percents, edgecolor = edgecolor, linewidth = 0.5, height = bgbarheight, color = bgbarcolor)
    texts = []
    for pct, bar in zip(percents, bars):
        y = bar.get_center()[1]
        inside_bar = pct/100 > label_inside_bar_cutoff
        alignment = 'right' if inside_bar else 'left'
        x = pct
        xoffset = -labeloffset if inside_bar else labeloffset
        txt = ax.annotate(
            f'{round(pct)}%', xy = (x, y), 
            xytext = (xoffset, 0), textcoords = 'offset points', 
            verticalalignment = 'center', horizontalalignment = alignment, 
            fontweight = 'bold' if inside_bar else 'medium', fontsize = labelfontsize,
            color = 'w' if inside_bar else 'k'
        )
        if inside_bar:
            add_outline(txt)
        texts.append(txt)
    ax.set(
        xlim = (0, 100),
        xticks = ticks, xticklabels = map(lambda x: f'{int(x)}%', ticks)
    )
    if not show_x_axis:
        ax.xaxis.set_visible(False)
        ax.spines['bottom'].set_visible(False)
    for spine in ['left', 'right', 'top']:
        ax.spines[spine].set_visible(False)
    ax.yaxis.set_tick_params(left = False)
    return (bars, bgbars, texts)

# Artist hierarchy inspection.
# Use these for detailed insights into matplotlib layout
def inspect_layout(artist: Artist, handler = lambda artist, depth, index: None, depth = 0, index = 0):
    handler(artist, depth, index)
    for index, child in enumerate(artist.get_children()):
        inspect_layout(child, handler, depth = depth + 1, index = index)

def print_layout(artist: Artist): # to do: add maximum depth or filters as needed to curb verbose output
    def handle_artist(artist, depth, index):
        artist_description = str(artist)
        if hasattr(artist, 'get_bbox'):
            artist_description += f': {artist.get_bbox()}'
        print('| ' * depth + f'{index+1}. ' + artist_description)
    inspect_layout(artist, handle_artist)

def show_layout(artist: mpl.artist.Artist, facecolor = ('y', 0.05), depth = 0):
    def handle_artist(artist, depth, index):
        if hasattr(artist, 'set_facecolor'):
            if not artist.get_facecolor():
                artist.set_facecolor(facecolor)
        elif isinstance(artist, Text):
            artist.set_bbox({ 'facecolor': facecolor})
    inspect_layout(artist, handle_artist)

def set_style():
    """
    Configure default matplotlib styling used throughout the project.
    """
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['savefig.transparent'] = True
    plt.rcParams['savefig.dpi'] = 300
    #plt.rcParams['savefig.pad_inches'] = 0.1
    #plt.rcParams['figure.constrained_layout.use'] = True
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

def plot_ratings(
    ratings: pd.Series,
    include_title = True,
    style = 'percent', # options: 'percent' or 'bars'. Percent styling adds a gray backgground bar to each star rating that reaches to 100%, reusing our rate widget.
    color = None,
):
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

    if style == 'percent':
        plot_rates(y, x, color = color)
        max_pct = 100
    else:
        bars = barh(
            y, x, color = color
        )
        max_pct = x.max()
        for bar, pct, _y in zip(bars, x, y):
            offset = 4
            text = plt.annotate(
                to_percent(pct),
                xy = (pct, _y),
                xytext = (offset, 0), textcoords = 'offset points',
                verticalalignment = 'center',
                horizontalalignment = 'left',
                fontsize = 13,
                fontweight = 'medium',
                color = 'k'
            )
    ax = plt.gca()
    ax.set(
        yticks = y, yticklabels = map(rating_to_stars_string, y),
        xticks = [], 
        xlim = [0, max_pct]
    )
    ax.yaxis.set_tick_params(labelsize = 15)
    if include_title:
        ax.set_title(f'({ratings_str})')
    ax.yaxis.set_tick_params(left = False)
    for spine in ['top', 'bottom', 'left', 'right']:
        ax.spines[spine].set_visible(False)
    ax.margins(0.2, 0)
    if include_title:
        plt.suptitle(f'        {stars_str}', fontsize = 21)

    # enable to debug inspect layout
    #ax.set_facecolor(('k', 0.1))
    #ax.figure.set_facecolor(('k', 0.1))