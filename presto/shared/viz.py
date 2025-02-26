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
import numpy as np
import pandas as pd
import seaborn as sns

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
    percents = np.array([x * 100 for x in width])
    bars = ax.barh(y, percents, height = barheight, left = 1, edgecolor = edgecolor, linewidth = 0.5, color = color)
    bgbars = ax.barh(y, [100 - x - 2 for x in percents], left = percents + 1, edgecolor = edgecolor, linewidth = 0.5, height = bgbarheight, color = bgbarcolor)
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
        #if hasattr(artist, 'get_bbox'):
        #    artist_description += f': {artist.get_bbox()}'
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
    # General settings
    #plt.rcParams['font.family'] = 'Arial' # does not support rating stars
    plt.rcParams['font.size'] = 13
    plt.rcParams['font.weight'] = 'regular'
    plt.rcParams['font.stretch'] = 'normal'     # normal | (semi|extra|ultra)?condensed | (semi|extra|ultra)?expanded
    #plt.rcParams['savefig.transparent'] = True
    plt.rcParams['savefig.dpi'] = 300

    # Component-specific settings
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    #plt.rcParams['savefig.pad_inches'] = 0.1
    #plt.rcParams['figure.constrained_layout.use'] = True
    #plt.rcParams['figure.dpi'] = 100
    #plt.rcParams['figure.facecolor'] = ('b', 5/255) # Add a slight hint of color for branding and for layout transparency
    #plt.rcParams['figure.figsize'] = [6.4, 4.8]
    plt.rcParams['figure.titlesize'] = 25
    plt.rcParams['figure.titleweight'] = 'bold'
    #plt.rcParams['axes.grid'] = False
    #plt.rcParams['axes.labelpad'] = 4.0
    #plt.rcParams['axes.labelsize'] = 'medium'
    #plt.rcParams['axes.labelweight'] = 'normal'
    #plt.rcParams['axes.linewidth'] = 0.8
    #plt.rcParams['axes.titlecolor'] = 'auto'
    #plt.rcParams['axes.titlelocation'] = 'left'
    #plt.rcParams['axes.titlepad'] = 6.0
    #plt.rcParams['axes.titlesize'] = 21
    #plt.rcParams['axes.titleweight'] = 'normal'
    #plt.rcParams['axes.titley'] = None
    #plt.rcParams['grid.color'] = '#b0b0b0'
    #plt.rcParams['grid.alpha'] = 1.0
    #plt.rcParams['grid.linestyle'] = '-'
    #plt.rcParams['grid.linewidth'] = 0.8
    plt.rcParams['svg.fonttype'] = 'none' # path | none. set to None to use true text in SVG instead of rasterizing text

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

##############
# RATINGS
##############
def rating_to_stars_string(rating) -> str:
    full_stars = math.floor(rating)
    # to do: handle fractional stars (another dataset has them, and they can be the result of aggregates)
    return '★' * full_stars

def plot_ratings(
    ratings: pd.Series,
    style = 'percent', # options: 'percent' or 'bars'. Percent styling adds a gray backgground bar to each star rating that reaches to 100%, reusing our rate widget.
    color = None,

    rating_label_size = 15,
    percent_label_size = 13,

    include_title = True,
    title_size = 21,
    title_y = 1.1,
    subtitle_size = 12,
    subtitle_pad = 15
):
    # get counts per rating
    counts = ratings.value_counts(normalize = True).sort_index(ascending = True)
    for i in range(1,6):
        # insert missing zero counts so that they are spelled out in the final plot
        if float(i) not in counts.index:
            counts[i] = 0
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
                fontsize = percent_label_size,
                fontweight = 'medium',
                color = 'k'
            )
    ax = plt.gca()
    ax.set(
        yticks = y, yticklabels = map(rating_to_stars_string, y),
        xticks = [], 
        xlim = [0, max_pct * 1.01] # use slight upscale on x axis to prevent clipping 
    )
    ax.yaxis.set_tick_params(labelsize = rating_label_size)
    if include_title:
        ax.set_title(f'({ratings_str})', fontsize = subtitle_size, pad = subtitle_pad)
    ax.yaxis.set_tick_params(left = False)
    for spine in ['top', 'bottom', 'left', 'right']:
        ax.spines[spine].set_visible(False)
    ax.margins(0.2, 0)
    if include_title:
        fig = ax.figure
        fig.subplots_adjust(left = 0.1, right = 0.9) # make figure symmetrical so that suptitle will center-align
        txt = plt.suptitle(f'{stars_str}', fontsize = title_size, y = title_y)
        #txt.set_fontsize(title_size)

    # enable to debug inspect layout
    #ax.set_facecolor(('k', 0.1))
    #ax.figure.set_facecolor(('k', 0.1))


#########################
# User Review Matrices
# For showing product similarities based on user reviews
#########################

title_font_size = 15
subtitle_font_size = 12
colorbar_font_size = 15
axis_font_size = 13
subtitle_color = ('k', 0.66)

def highlight_active_product(axis, data, product_id):
    labels = axis.get_ticklabels()
    product_idx = list(data.index).index(product_id)
    #product_idx = labels.index(product_id)
    if product_idx != None:
        target_label = labels[product_idx]
        target_label.set_fontweight('bold')

def add_title_and_subtitle(ax, title, subtitle):
    title_text = ax.set_title(title, fontsize = title_font_size, loc = 'left', pad = 32)
    #subtitle_text = ax.text(0, 1, subtitle, fontsize = subtitle_font_size, color = subtitle_color)
    subtitle_text = ax.annotate(
        subtitle, 
        xy = (0,1), xycoords = 'axes fraction', verticalalignment = 'bottom', 
        xytext = (0, 14), textcoords = 'offset points',
        fontsize = subtitle_font_size, color = subtitle_color
    )
    return title_text, subtitle_text

def truncate_text(text: str, limit: int, trunc = '…') -> str:
    if len(text) > limit:
        return text[:limit] + trunc
    return text

def plot_user_ratings_by_product(
        data: pd.DataFrame, 
        target_product_id: str, # to highlight the active / target product 
        conn, 
        cbar_kws = None,
        product_name_limit = 20,
        hide_y_axis_cutoff = 50,
        hide_x_axis_cutoff = 500
):    
    """
    Given a pivot table of rows = product ids, columns = user ids, and cells = ratings, 
    plot a heat map of product reviews by users
    """
    cmap = mpl.colormaps.get_cmap('Blues')
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    # create heatmap
    result = sns.heatmap(data, vmin = 0, vmax = 5, cmap = cmap, norm = norm, cbar_kws = cbar_kws)

    # customize rating colorbar
    colorbar = result.collections[0].colorbar
    colorbar.set_label("Rating", fontsize = colorbar_font_size)
    colorbar.set_ticks(range(0,6))
    colorbar.set_ticklabels(['None', '★', '★★', '★★★', '★★★★', '★★★★★'], fontsize = 15)
    colorbar.outline.set_visible(True)
    colorbar.outline.set_color('k')
    colorbar.ax.spines[:].set_visible(True)
    result.spines[:].set_visible(True)

    # customize main chart
    product_names = data.index.map(lambda name: truncate_text(name, product_name_limit))
    result.yaxis.set_ticklabels(product_names.values, fontsize = axis_font_size)
    result.yaxis.label.set_visible(False)
    plt.xlabel('User', fontsize = axis_font_size, labelpad = 12)
    txt = result.xaxis.set_label_text('User', fontsize = axis_font_size, horizontalalignment = 'left', x = 0)
    #txt.set_position((1, 1))
    result.xaxis.set_ticklabels([f'U{i+1}' for i in range(len(data.columns))], fontsize = axis_font_size)
    add_title_and_subtitle(result, 'User Ratings Per Product', 'Rows are ratings by individual users')
    
    highlight_active_product(result.yaxis, data, target_product_id)

    if data.shape[1] >= hide_x_axis_cutoff:    
        result.xaxis.set_visible(False)
    if data.shape[0] >= hide_y_axis_cutoff:
        result.yaxis.set_visible(False)
    
    return result

#plot_user_ratings_by_product(user_ratings_per_product, product.id, conn)

def plot_pairwise_similarities(data: pd.DataFrame, id: str, conn, product_name_limit = 20, ax = None, cbar_kws = None, title_fontsize = 15, cbar_fontsize = 15, axis_fontsize = 13):
    """
    Given a square table of pairwise product similarities, show a product similarity heatmap.
    """
    ax = ax or plt.gca()
    ax = sns.heatmap(data, vmin = 0, vmax = 1, cmap = 'Reds', ax = ax, cbar_kws = cbar_kws)
    colorbar = ax.collections[0].colorbar
    colorbar.set_label('Product Similarity', fontsize = cbar_fontsize)
    colorbar.set_ticks([0, .25, .5, .75, 1])
    colorbar.set_ticklabels(['0', '25%', '50%', '75%', '100%'], fontsize = cbar_fontsize)
    for spine in ['top', 'bottom', 'left', 'right']:
        colorbar.ax.spines[spine].set_visible(True)
        ax.spines[spine].set_visible(True)
    colorbar_labels = colorbar.ax.yaxis.get_ticklabels()
    if len(colorbar_labels) > 1:
        colorbar_labels[0].set_verticalalignment('bottom')
        colorbar_labels[-1].set_verticalalignment('top')
    
    product_names = data.index.map(lambda name: truncate_text(name, product_name_limit))
    ax.xaxis.set_ticklabels(product_names, fontsize = axis_fontsize)
    ax.yaxis.set_ticklabels(product_names, fontsize = axis_fontsize)
    ax.set_title('Product Similarities', fontsize = title_fontsize, loc = 'left')
    add_title_and_subtitle(ax, 'Product Similarities', 'Pairwise similarity of rows of product reviews')
    ax.yaxis.label.set_visible(False)
    ax.xaxis.label.set_visible(False)

    # Highlight active product
    highlight_active_product(ax.yaxis, data, id)
    highlight_active_product(ax.xaxis, data, id)    

    return ax