from starlette.applications import Starlette
from starlette.responses import Response, RedirectResponse
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from web import ipc

templates = Jinja2Templates(directory="web/templates")
client = ipc.Client()

bot_name = "nextcord.example"

async def start():
    await client.initiate()
    
async def stop():
    await client.close()
    
async def index(request: Request) -> Response:
    stats = await client.request("stats")
    return templates.TemplateResponse(
        "index.html", context={"request": request, "name": bot_name, "stats": stats}
    )
    
async def not_found(request, exc):
    return templates.TemplateResponse("404.html", context={"request": request})

async def test(r):
    e = await client.request("test", text="test")
    return Response(e)

routes = [
    Route("/", endpoint=index),
    Route("/stats", endpoint=test),
    Mount("/static", StaticFiles(directory="web/static")),
]

exceptions = {404: not_found}

app = Starlette(
    debug=False, routes=routes, exception_handlers=exceptions, on_startup=[start], on_shutdown=[stop]
)