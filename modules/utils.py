import ROOT
import pandas as pd
import numpy as np
import functools
import log

def get_collection_quantities(coll_name, quantities):
    return [f'{coll_name}_{quantity}' for quantity in quantities]


def tree_to_df(tree, collection, quantities, global_query, trusty_quant):
    coll_quantities = get_collection_quantities(collection, quantities)
    array_dict = tree.arrays(library = 'np', filter_name = coll_quantities)
    nparticle = map(
        lambda x: len(x), 
        array_dict[f'{collection}_{trusty_quant}']
    )
    new_index_tuples = []
    for i, n in enumerate(nparticle):
        new_index_tuples.extend([
            (i, j)
            for j in range(n)
        ])
    new_index = pd.MultiIndex.from_tuples(new_index_tuples)

    array_dict = {
        key.split('_')[1]: np.hstack(val) # flatten the arrays
        for key, val in array_dict.items()
    }

    return pd.DataFrame(array_dict, index = new_index).query(global_query)

def combine_selections(sels1, sels2):
    return {
        f'{name1}_{name2}': f'({sel1}) & ({sel2})'
        for name1, sel1 in sels1.items()
        for name2, sel2 in sels2.items()
    }

def make_pt_selections(pt_values):
    return {f'pt{pt}': f'pt >= {pt}' for pt in pt_values}


def compose(*functions):
    return functools.reduce(
        lambda acc, f: lambda x, **kwargs: f(acc(x, **kwargs), **kwargs),
        functions,
        lambda x, **kwargs: x
    )

def keep_2_leading_electrons(df, trusty_quant = 'pt', **kwargs):
    all_event_indices = np.unique([i for i,j in df.index])
    
    # print(f'number of events: {len(all_event_indices)}')
    events = []
    event_indices = []
    for i in all_event_indices:
        event = df.loc[i,:]
        n_ele = len(event.loc[:,trusty_quant])

        if n_ele <= 2: continue

        events.append(
            (event
                .sort_values(by = 'pt', ascending = False, ignore_index = True)
                .head(2))
        )
        event_indices.append(i)
        
    try:
        return pd.concat(events, keys = event_indices)
    except ValueError:
        return pd.DataFrame({
            col: []
            for col in df.columns
        })

def event_invariant_mass(event):
    pts, etas, phis, energies = [event[q] for q in ['pt', 'eta', 'phi', 'energy']]
    try:
        return np.sum([
            ROOT.Math.PtEtaPhiEVector(pt, eta, phi, energy) 
            for pt, eta, phi, energy in zip(pts, etas, phis, energies)
        ]).M()
    except TypeError:
        return ROOT.Math.PtEtaPhiEVector(pts, etas, phis, energies).M()

def particle_number(event):
    return len(event['pt'])


def combine_dicts(d1, d2):
    return {**d1, **d2}