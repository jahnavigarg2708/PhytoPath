import os
import pandas as pd
import hashlib

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(key):
    hashed = hashlib.md5(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{hashed}.pkl")

def load_cache(key):
    path = _cache_path(key)
    if os.path.exists(path):
        return pd.read_pickle(path)
    return None

def save_cache(key, df):
    path = _cache_path(key)
    df.to_pickle(path)