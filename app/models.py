import pymongo
import asyncio

from typing import Optional, Callable, Awaitable, Coroutine

from bson import ObjectId
from easydict import EasyDict
from motor import motor_asyncio

__all__ = ['Text']


def object_action(f) -> Callable[..., Awaitable]:
    async def wrapper(self, *args, **kwargs) -> Object:
        await f(self, *args, **kwargs)
        self._set_kwargs_id()
        return self

    return wrapper


class ExtractFields:
    FIELDS = {}

    @property
    def fields(self) -> dict:
        return {k: v() for k, v in self.FIELDS.items()}


class Object:
    class Model(ExtractFields):
        __collection__ = None
        FIELDS = {'_id': ObjectId}
        INDEXES = {}

        def __init__(self, db: motor_asyncio.AsyncIOMotorDatabase, collection: str):
            self.collection: motor_asyncio.AsyncIOMotorCollection = db[collection]

        def __repr__(self) -> str:
            return f'<{self.__class__.__name__} ObjectModel>'

        def q(self, q: Optional[dict] = None, with_fields: bool = False, **kw) -> dict:
            return {**(self.fields if with_fields else {}),
                    **{k: self.FIELDS[k](v) if k in self.FIELDS else v for k, v in {**kw, **(q or {})}.items()}}

        def find_one(self, query: Optional[dict] = None, **kwargs):
            return self.collection.find_one(self.q(query, **kwargs))

        def find(self, query: Optional[dict] = None, **kwargs):
            return self.collection.find(self.q(query, **kwargs))

        def update_one(self, query: Optional[dict] = None, **search):
            def handler(data: dict = None, **kwargs):
                return self.collection.update_one(self.q(query, **search), {'$set': self.q(data, **kwargs)})

            return handler

        def update(self, query: Optional[dict] = None, **search):
            def handler(data: Optional[dict] = None, **kwargs):
                return self.collection.update_many(self.q(query, **search), {'$set': self.q(data, **kwargs)})

            return handler

        def delete_one(self, query: Optional[dict] = None, **kwargs):
            return self.collection.delete_one(self.q(query, **kwargs))

        def delete(self, query: Optional[dict] = None, **kwargs):
            return self.collection.delete_many(self.q(query, **kwargs))

        def insert_one(self, query: Optional[dict] = None, **kwargs):
            return self.collection.insert_one(self.q(query, with_fields=True, **kwargs))

        def insert(self, *args):
            return self.collection.insert_many(*(self.q(i, with_fields=True) for i in args))

        def count(self, query: Optional[dict] = None, **kwargs) -> int:
            return self.collection.count_documents(self.q(query, **kwargs))

        async def create_indexes(self) -> list:
            return [await self.collection.create_index(k, **v) for k, v in self.INDEXES.items()]

        async def check_indexes(self) -> bool:
            if len(await self.collection.index_information()) < 2:
                await self.create_indexes()
                return True
            else:
                return False

        async def object(self, *args, **kwargs) -> EasyDict:
            return EasyDict(await self.find_one(*args, **kwargs))

        async def objects(self, *args, **kwargs) -> tuple:
            return tuple(EasyDict(obj) for obj in await self.find(*args, **kwargs))

    def __init__(self, db: motor_asyncio.AsyncIOMotorDatabase, **kwargs):
        self.db = db
        self.model = self.Model(db, self.Model.__collection__ or self.__class__.__name__)
        self.kwargs = kwargs
        self.data = EasyDict()

    def __repr__(self):
        return f'<{self.__class__.__name__} Object>'

    @property
    def id(self) -> ObjectId:
        return self.data.get('_id')

    async def find(self, **kwargs) -> list:
        objects = []

        for data in await self.model.objects(**(kwargs or self.kwargs)):
            obj = self.__class__(self.db)
            obj.data = data.copy()
            objects.append(obj)

        return objects

    @object_action
    async def new(self) -> None:
        insert = await self.model.insert_one(self.kwargs, **self.data)
        await asyncio.gather(self.load(_id=insert.inserted_id), self.model.create_indexes())

    @object_action
    async def load(self, **kwargs) -> None:
        self.data = await self.model.object(**(kwargs or self.kwargs))

    @object_action
    async def save(self) -> None:
        await (self.model.update_one(self.kwargs)(self.data) if self.data else self.new())

    @object_action
    async def delete(self) -> None:
        await self.model.delete_one(self.kwargs)
        self.data = self.data.__class__()

    def _set_kwargs_id(self):
        self.kwargs = EasyDict(_id=self.id)


class Text(Object):
    class Model(Object.Model):
        __collection__ = 'texts'
        FIELDS = {**Object.Model.FIELDS, 'parent': ObjectId, 'text': str}
        INDEXES = {
            (('parent', pymongo.DESCENDING),): {'background': True},
            (('text', pymongo.TEXT), ): {'unique': False, 'background': True}
        }

    @property
    def parent(self) -> Coroutine:
        return self.__class__(self.db, _id=self.data.parent).load()
