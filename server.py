import uvicorn
from web.app import app
import logging

log = logging.getLogger("runner.server")

if __name__ == "__main__":
    try:
        import uvloop
    except ModuleNotFoundError:
        log.warning("uvloop is not installed")
    else:
        uvloop.install()
    connect_kwargs = {"use_colors": False, "host": "localhost"}
    config = uvicorn.Config(app, **connect_kwargs)
    server = uvicorn.Server(config)

    server.run()