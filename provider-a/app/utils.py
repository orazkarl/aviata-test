import json
from functools import lru_cache


@lru_cache()
def get_file(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)
