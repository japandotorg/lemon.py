import asyncio
from typing import Any, Optional
import aiohttp
import aiohttp.web
from traceback import format_exception
from aiohttp.client_exceptions import ClientConnectionError
import logging

client = logging.getLogger("ip_client")
server = logging.getLogger("ip_server")

class Client:
    def __init__(self, host: str = "localhost", port: int = 6666, key="very secret key"):
        self.loop = asyncio.get_event_loop()
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket = None
        
        self.host = host
        self.port = port
        self.key = key
        
    @property
    def url(self):
        return f"ws://{self.host}:{self.port}"
    
    async def request(self, endpoint: str, **kwargs) -> Any:
        if self.websocket is None:
            return None
        client.info(f"Requesting IPC Server for {endpoint}")
        
        payload = {"endpoint": endpoint, "auth": self.key, "kwargs": kwargs}
        await self.websocket.send_json(payload)
        
        recv = await self.websocket.receive()
        
        if recv.type == aiohttp.WSMsgType.PING:
            client.info("Recieved request to PING")
            await self.websocket.ping()
            
            return await self.request(endpoint, **kwargs)
        
        if recv.type == aiohttp.WSMsgType.PONG:
            client.info("Received PONG")
            return await self.request(endpoint, **kwargs)
        
        if recv.type == aiohttp.WSMsgType.CLOSED:
            client.error("WebSocket connection closed.")
            await self.session.close()
            await asyncio.sleep(5)

            while self.websocket is None:
                await self.initiate()
            return await self.request(endpoint, **kwargs)

        return recv.json()

    async def initiate(self):
        client.info("Instantiating websocket.")
        self.session = aiohttp.ClientSession()

        try:
            self.websocket = await self.session.ws_connect(self.url, autoclose=False, autoping=False)
        except ClientConnectionError:
            pass

    async def close(self):
        await self.session.close()
        await self.websocket.close()
        
class Server:
    ENDPOINTS = {}

    def __init__(self, bot, host: str = "localhost", port: int = 6666, key="very secret key"):
        self.loop = asyncio.get_event_loop()
        self._server = None

        self.bot = bot
        self.host = host
        self.port = port
        self.key = key

    async def __start__(self):
        runner = aiohttp.web.AppRunner(self._server)
        await runner.setup()

        site = aiohttp.web.TCPSite(runner, self.host, self.port)
        await site.start()

    def start(self):
        self._server = aiohttp.web.Application()
        self._server.router.add_route("GET", "/", self.handle_ws)

        self.loop.run_until_complete(self.__start__())

    async def handle_json(self, ws, json: dict):
        if json.get("auth") != self.key:
            server.warning("Recieved unauthorized request.")
            response = {"error": "Invalid token provided", "code": 403}
        else:
            endpoint = json.get("endpoint")
            func = self.ENDPOINTS.get(endpoint)
            if not endpoint:
                server.info("Received a request with no endpoint.")
                response = {"error": "No Endpoint Provided", "code": 400}
            elif func is None:
                response = {"error": "Invalid Endpoint provided", "code": 400}
            else:
                cog = self.bot.get_cog(func.__qualname__.split(".", maxsplit=1)[0])
                kwargs = json["kwargs"]
                args = [cog, kwargs] if cog else [self.bot, kwargs]
                if kwargs == {}:
                    del args[1]

                try:
                    response = await func(*args)
                except Exception as err:
                    server.error(f"Recieved error while executing {err}")
                    response = {"error": f"IPC route raised error of type {type(err).__name__}", "code": 500}

        try:
            await ws.send_json(response)
        except TypeError as error:
            if str(error).startswith("Object of type") and str(error).endswith("is not JSON serializable"):
                server.error("IPC route returned values which are not able to be sent over sockets.")

                response = {
                    "error": "IPC route returned values which are not able to be sent over sockets.",
                    "code": 500,
                }

                await ws.send_json(response)

    async def handle_ws(self, request):
        ws = aiohttp.web.WebSocketResponse()
        await ws.prepare(request)

        async for data in ws:
            json = data.json()

            await self.handle_json(ws, json)


def route(name=None):
    def deco(func):
        if not name:
            Server.ENDPOINTS[func.__name__] = func
        else:
            Server.ENDPOINTS[name] = func

    return deco