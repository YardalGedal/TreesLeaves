import asyncio

from aiohttp import web
from motor import motor_asyncio

from . import http
from . import config

__all__ = ['run']

PORT = 8888

ROUTES = [
    web.get('/new', http.new),
    web.get('/search', http.search),
    web.get('/get', http.get)
]


def run() -> None:
    app = create_app(ROUTES)
    web.run_app(app, port=PORT, reuse_port=True)


def create_app(routes: list or tuple, app_vars: dict = None, **kwargs) -> web.Application:
    app_vars = app_vars or {}

    if not app_vars.get('db'):
        app_vars['db'] = motor_asyncio.AsyncIOMotorClient(
            config.DB_HOST, config.DB_PORT, io_loop=asyncio.get_event_loop()
        )[config.DB_NAME]

    app = web.Application(**kwargs)
    for k, v in app_vars.items():
        app[k] = v
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    run()
