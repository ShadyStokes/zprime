import json
from types import SimpleNamespace

with open(f'../config.json', 'r') as cfg:
    config = json.loads(
        cfg.read(),
        object_hook=lambda d: SimpleNamespace(**d)
    )

