import utils

class Quantity:
    def __init__(self, bins = 100, range = None, histo = None, calc = None):
        self.bins = bins
        self.range = range
        self.calc = calc
    
    def to_dict(self):
        return {'bins': self.bins, 'range': self.range}
    
    def __getitem__(self, item):
        return self.to_dict().__getitem__(item)

    def keys(self):
        return self.to_dict().keys()

default_histo_params = {'bins': 50, 'range': None}

def adjust_quantities(quantities, default = default_histo_params):
    if quantities is None:
        return {}
    if isinstance(quantities, list):
        return {q_name: default for q_name in quantities}
    return {
        q_name: utils.combine_dicts(default, q) if isinstance(q, dict) else (default if q is None else q)
        for q_name, q in quantities.items()
    }

class Filler:
    def __init__(self, name = '', modifiers = None, collect = None, calculate = None, selections = None, using_default = None, **kwargs):
        self.name = name

        self.modifiers = [] if modifiers is None else modifiers

        self.collect = adjust_quantities(collect)

        self.calculate = adjust_quantities(
            calculate, 
            default = Quantity(**default_histo_params)
        )

        self.selections = {} if selections is None else selections

        if using_default is not None:
            self.collect = utils.combine_dicts(
                using_default.collect, self.collect
            )
            self.calculate = utils.combine_dicts(
                using_default.calculate, self.calculate
            )
            self.selections = utils.combine_dicts( 
                using_default.selections, self.selections
            )
            if len(self.modifiers) == 0:
                self.modifiers = using_default.modifiers
    
    def using_default(self, filler):
        return Filler(
            self.name,
            modifiers = filler.modifiers if len(self.modifiers) == 0 else self.modifiers,
            collect = utils.combine_dicts(
                filler.collect, self.collect
            ),
            calculate = utils.combine_dicts(
                filler.calculate, self.calculate
            ),
            selections = utils.combine_dicts(
                filler.selections, self.selections
            ),
        )
    
    def add(self, modifiers = [], collect = {}, calculate = {}, selections = {}):
        return Filler(
            self.name,
            modifiers = self.modifiers + modifiers,
            collect = utils.combine_dicts(
                self.collect, collect
            ),
            calculate = utils.combine_dicts(
                self.calculate, calculate
            ),
            selections = utils.combine_dicts(
                self.selections, selections
            )
        )

    def add_mod(self, modifiers = []):
        return self.add(modifiers = modifiers)
    
    def add_coll(self, collect = {}):
        return self.add(collect = collect)
    
    def add_calc(self, calculate = {}):
        return self.add(calculate = calculate)
    
    def add_sels(self, selections = {}):
        return self.add(selections = selections)
    
    def set(self, modifiers = None, collect = None, calculate = None, selections = None):
        return Filler(
            self.name,
            modifiers = self.modifiers if modifiers is None else modifiers,
            collect = self.collect if collect is None else collect,
            calculate = self.calculate if calculate is None else calculate,
            selections = self.selections if selections is None else selections
        )
    
    def set_mod(self, modifiers = {}):
        return self.set(modifiers = modifiers)
    
    def set_coll(self, collect = {}):
        return self.set(collect = collect)
    
    def set_calc(self, calculate = {}):
        return self.set(calculate = calculate)
    
    def set_sels(self, selections = {}):
        return self.set(selections = selections)
    
    def without(self, collect = [], calculate = [], selections = []):
        return Filler(
            self.name,
            collect = {
                key: val for key, val in self.collect.items() 
                if key not in collect
            },
            calculate = {
                key: val for key, val in self.calculate.items() 
                if key not in calculate
            },
            selections = {
                key: val for key, val in self.selections.items() 
                if key not in selections
            },
        )
    
    def items(self):
        return utils.combine_dicts(self.collect, self.calculate).items()
    
    def __repr__(self):
        return '\n'.join([
            f'filler <{self.name}>',
            f'quantities to be collected:\n\t{self.collect}',
            f'quantities to be calculated:\n\t{self.calculate}',
            f'selections to be queried:\n\t{self.selections}'
        ]) + '\n'

TkEleEB = Filler(
    'TkEleEB',
    collect = {
        'pt': {'range': (0, 1200)},
        'eta': {'range': (-1.6, 1.6)},
        'phi': {'range': (-4, 4)},
        'energy': {'range': (0, 2500)}
    }
)

TkEleEE = Filler(
    'TkEleEE',
    collect = {
        'eta': {'range': (-3, 3)}
    },
    using_default = TkEleEB
)

gen = Filler(
    'gen',
    collect = {
        'pt': {'range': (0, 3500)},
        'eta': {'range': (-1.6, 1.6)},
        'phi': {'range': (-4, 4)},
        'energy': {'range': (0, 7000)},
        'pdgid': {'range': (-1000, 1000)},
        'status': {'bins': 80, 'range': (0, 80)}
    }
)

simpart = Filler(
    'simpart',
    using_default = gen.without(
        collect = ['pdgid', 'status']
    )
)

def get_mass_calc(bins = default_histo_params['bins'], range = default_histo_params['range'], name = 'mass'):
    return {
        name: Quantity(
            bins = bins,
            range = range,
            calc = utils.event_invariant_mass
        )
    }
