from yaml import safe_load

__all__ = (
    "token",
    "prefix",
    "postgres_uri",
)

with open("config.yml") as f:
    _config = safe_load(f)
    
token = _config["token"]
prefix = _config["prefix"]
postgres_uri = _config["postgres_uri"]

del _config