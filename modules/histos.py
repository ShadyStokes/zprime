import numpy as np
import uproot
import utils
import fill


def get_histo(content, bins = 50, range = None):
    result, _ = np.histogram(content, bins = bins, range = range)
    return result


def get_histo_name(*args):
    return '_'.join(args)

class Histos:
    def __init__(self, fillers = None, default = None, omit = None):
        if default is None: default = fill.Filler()

        if fillers is None: fillers = fill.Filler()

        self.fillers = list(map(
            lambda col: (
                fill.Filler(name = col) if isinstance(col, str) else col
            ).using_default(default),
            fillers
        ))

        self._histos = {
            get_histo_name(filler.name, sel_name, q_name): np.histogram([], **q_params)
            for filler in self.fillers
            for q_name, q_params in filler.items()
            for sel_name, _ in filler.selections.items()
            if q_name not in omit
        }

        self.omit = [] if omit is None else omit
    
    def __getitem__(self, item):
        return self._histos.__getitem__(item)
    
    def __setitem__(self, item, value):
        self._histos.__setitem__(item, value)
    
    def __iter__(self):
        return iter(self._histos.items())
    
    def add(self, histo_name, histo):
        old_counts, bin_edges = self[histo_name]
        self[histo_name] = (old_counts + histo, bin_edges)

    
    def fill(self, tree, global_query = '', trusty_quant = 'pt', verbose = True, **modifier_kwargs):

        for filler in self.fillers:
            if verbose: print(f'filler {filler.name}')

            modify = utils.compose(*filler.modifiers)

            df = modify(
                utils.tree_to_df(
                    tree, filler.name, list(filler.collect), global_query, trusty_quant
                ),
                **utils.combine_dicts(
                    {'global_query': global_query, 'trusty_quant': trusty_quant}, 
                    modifier_kwargs
                )
            )

            for sel_name, sel in filler.selections.items():
                if verbose: print(f'selection {sel_name}')

                # if sel.is_blacklisted(filler.name): continue

                sel_df = df.query(sel)

                for q_name, q_params in filler.collect.items():
                    if q_name in self.omit: continue

                    self.add(
                        get_histo_name(filler.name, sel_name, q_name), 
                        get_histo(sel_df[q_name], **q_params)
                    )

                event_indices = np.unique([i for i,j in sel_df.index])

                for q_name, q in filler.calculate.items():
                    arr = np.array([
                        q.calc(sel_df.loc[idx,:]) 
                        for idx in event_indices
                    ]).flatten()

                    self.add(
                        get_histo_name(filler.name, sel_name, q_name), 
                        get_histo(arr, **q)
                    )
    
    def save(self, file):
        with uproot.recreate(file) as output:
            for q_name, q in self:
                output[q_name] = q
    
    def quantity_list(self):
        return list(self._quantities)

