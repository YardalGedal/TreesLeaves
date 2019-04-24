from aiohttp import web

from . import actions

__all__ = ['new', 'search', 'get']


async def new(request: web.Request) -> web.Response:
    return web.json_response(text=str(await actions.new(
        request.app['db'], request.query.get('text'), request.query.get('parent')
    )))


async def search(request: web.Request) -> web.Response:
    return web.json_response(text=str(await actions.search(
        request.app['db'], request.query.get('text')
    )))


async def get(request: web.Request) -> web.Response:
    return web.json_response(text=str(await actions.get(
        request.app['db'], request.query.get('id')
    )))
