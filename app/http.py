from typing import Callable
from typing import Awaitable

from aiohttp import web

from . import actions
from .results import Result

__all__ = ['new', 'search', 'get']


async def new(request: web.Request) -> web.Response:
    return await make_response(actions.new, request.app['db'], request.query.get('text'), request.query.get('parent'))


async def search(request: web.Request) -> web.Response:
    return await make_response(actions.search, request.app['db'], request.query.get('text'))


async def get(request: web.Request) -> web.Response:
    return await make_response(actions.get, request.app['db'], request.query.get('id'))


async def make_response(f: Callable[[web.Request], Awaitable[Result]], *args, **kwargs):
    return web.json_response(text=str(await f(*args, **kwargs)))
