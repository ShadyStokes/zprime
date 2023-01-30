import matplotlib.pyplot as plt
import numpy as np
import functools
import re
# import os
import utils


class HistoDetails:
    def __init__(self, full_name, collection, selections, quantity):
        self.full_name = full_name
        self.collection = collection
        self.selections = selections
        self.quantity = quantity

def std_name_cleaner(histo_name):
    return histo_name.split(';')[0]

def std_histo_name_parser(
    histo_name, delimiter = '_', name_cleaner = std_name_cleaner
):
    clean_histo_name = name_cleaner(histo_name)
    split_histo_name = clean_histo_name.split(delimiter)

    return HistoDetails(
        full_name = clean_histo_name,
        collection = split_histo_name[0],
        selections = split_histo_name[1:-1],
        quantity = split_histo_name[-1]
    )


class Plotter:
    def __init__(self, match = None, params = None, draw_func = None):
        self.match = (lambda name: False) if match is None else match
        if isinstance(match, str):
            regex = re.compile(match)
            self.match = lambda histo_details: False if regex.match(histo_details.full_name) is None else True
        self.params = {} if params is None else params
        self.draw_func = draw_func
    
    def using_default(self, default):
        return Plotter(
            match = self.match,
            params = utils.combine_dicts(
                default.params, self.params
            ),
            draw_func = self.draw_func
        )
    
    def draw(self, artist, histo_name, histo, **params):
        if self.draw_func is not None:
            self.draw_func(
                artist, histo_name, histo,
                **utils.combine_dicts(
                    self.params,
                    params
                )
            )


class Artist:
    def __init__(
        self, plotters = None, default = Plotter(), output_dir = None, 
        express_plotters = None, label_dict = None,
        name_parser = None,
    ):
        plotters = [default] if plotters is None else plotters
        self.plotters = [
            plotter.using_default(default)
            for plotter in plotters
        ]

        self.output_dir = output_dir

        self.name_parser = std_histo_name_parser if name_parser is None else name_parser

        self.express_plotters = {} if express_plotters is None else express_plotters

        self.label_dict = {} if label_dict is None else label_dict
    
    def draw(
        self, histo_name, histo, filepath = None, **draw_params
    ):
        # draw_params = {} if draw_params is None else draw_params
        histo_details = self.name_parser(histo_name)
        
        try:
            self.express_plotters[histo_details.full_name].draw(
                self, histo_details, histo, **draw_params
            )
        except KeyError:
            matching_plotters = [
                plotter for plotter in self.plotters
                if plotter.match(histo_details)
            ]

            params = functools.reduce(
                utils.combine_dicts, [
                    plotter.params for plotter in matching_plotters
                ] + [draw_params], 
                {}
            )

            if filepath is None and self.output_dir is not None:
                filepath = f'{self.output_dir}/{histo_details.full_name}'
            
            params = utils.combine_dicts(
                {'save_to': filepath},
                params
            )

            for plotter in matching_plotters:
                plotter.draw(
                    self, histo_details, histo, **params
                )
                

def generic_histo_drawing_func(
    artist, histo_details, histo, 
    figsize = (6,5), close_fig = True,
    color = 'black', linewidth = 1, title = None,
    alpha = 1, grid_alpha = 0.4, fill_alpha = 0.15,
    save_to = None, show = False, xlab = None, ylab = None,
    **params
):
    h, bins = histo.to_numpy()

    x = np.concatenate((np.array([bins[0]]), bins))
    y = np.concatenate((np.array([0]), h, np.array([0])))

    fig = plt.figure(figsize = figsize)

    plt.grid(alpha = grid_alpha)
    plt.step(
        x, y, where = 'pre', 
        color = color, linewidth = linewidth
    )
    plt.fill_between(
        x, y, step = "pre", 
        alpha = fill_alpha, color = color
    )
    xlab = histo_details.quantity if xlab is None else xlab
    try: xlab = artist.label_dict[xlab]
    except KeyError: pass

    ylab = 'count' if ylab is None else ylab 
    try: ylab = artist.label_dict[ylab]
    except KeyError: pass

    plt.xlabel(xlab)
    plt.ylabel(ylab)

    title = histo_details.full_name if title is None else title
    plt.title(title)

    if save_to is not None: plt.savefig(f'{save_to}.png')
    
    if show: plt.show()

    if close_fig: plt.close(fig)

def generic_histo_plotter(**params):
    return Plotter(
        match = lambda histo_details: True,
        params = params,
        draw_func = generic_histo_drawing_func
    )

label_dict = {
    'mass': 'Invariant Mass (GeV)',
    'pt': 'Transverse Momentum (GeV)'
}

def match_quantity(quantity):
    return lambda histo_details: histo_details.quantity == quantity

def match_collection(collection):
    return lambda histo_details: histo_details.collection == collection


# def generic_plotter(quantity)