import uproot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys; sys.path.insert(0, '../modules')
from system import config
import plotters

input_dir = f'{config.project_dir}/out/out'

input_file_name = 'histos_1'

artist = plotters.Artist(
    default = plotters.generic_histo_plotter(),
    label_dict = plotters.label_dict,
    output_dir = f'{config.project_dir}/plots/{input_file_name}'
)

with uproot.open(f'{input_dir}/{input_file_name}.root') as fin:
    for histo_name, histo in fin.items():
        print(f'making plots for {histo_name}')

        artist.draw(
            histo_name, histo,
            color = 'orangered',
            linewidth = 1.5
        )

