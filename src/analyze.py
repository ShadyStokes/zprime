import ROOT
import uproot
import numpy as np
import pandas as pd
import glob
import sys; sys.path.insert(0, '../modules')
from system import config
import utils
import histos
import fill
import log

TIME = log.Timer()

mass2500 = fill.get_mass_calc(range = (10, 2500))
mass7000 = fill.get_mass_calc(range = (10, 7000))

pt_sels = utils.make_pt_selections([45])

histograms = histos.Histos(
    fillers = [
        fill.TkEleEB.add_calc(mass2500),
        fill.TkEleEE.add_calc(mass2500),
        fill.gen.add_calc(mass7000).set(
            modifiers = [utils.keep_2_leading_electrons],
            selections = utils.combine_selections(
                {'fse': '(abs(pdgid) == 11) & (status == 1)'}, # final state electrons
                pt_sels
            )
        ),
        fill.simpart.add_calc(mass7000).set_mod([
            utils.keep_2_leading_electrons
        ])
    ],
    default = fill.Filler(
        selections = pt_sels
    ),
    omit = 'phi,energy,pdgid,status,eta'.split(',')
)

nfile = 0

for filename in glob.iglob(f'{config.ntuple_dir}/*.root'):
    print(f'opening file {nfile} ({filename})')
    with uproot.open(filename) as fin:
        for key, tree in fin.items():
            if '/' not in key: continue

            print(f'using tree {key}')
            histograms.fill(
                tree,
                global_query = 'pt >= 45' # abs(eta) <= 1.479
            )
            
            print(f'WRITING TO FILE ({TIME.elapsed()})')
            histograms.save(
                f'{config.project_dir}/out/histos_1.root'
            )
    
    nfile += 1


print(f'total time elapsed: {TIME.elapsed()}')