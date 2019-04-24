import asyncio
import bson.errors

from bson import ObjectId
from motor import motor_asyncio

from .results import *
from .models import Text

__all__ = ['new', 'search', 'get']


async def new(db: motor_asyncio.AsyncIOMotorDatabase, text: str, parent: str or ObjectId) -> Result:
    """
    as Result returns Error object TextNotPassed
    or Ok object with boolean value True
    """
    if not text:
        return TextNotPassed()

    text = await Text(db, text=text).new()

    if parent:
        try:
            text.data.parent = ObjectId(parent)
        except bson.errors.InvalidId:
            await text.delete()
            return InvalidId()
    else:
        text.data.parent = str(text.id)

    await text.save()

    return Ok(str(text.id))


async def search(db: motor_asyncio.AsyncIOMotorDatabase, text: str) -> Result:
    """
    as Result returns Error object TextNotPassed
    or Ok object with list of documents with their parents
    """
    if not text:
        return TextNotPassed()

    docs = await Text(db).model.collection.find({'$text': {'$search': text}}, {'score': {'$meta': 'textScore'}}).sort(
        [('score', {'$meta': 'textScore'})]
    ).to_list(10 ** 9)

    parents = await asyncio.gather(*(get_parents(db, i['_id']) for i in docs))

    return Ok([make_doc(i['_id'], i['text'], parents[n]) for n, i in enumerate(docs)])


async def get(db: motor_asyncio.AsyncIOMotorDatabase, _id: str or ObjectId) -> Result:
    """
    as Result returns Error object NothingFound
    or Ok object, contains document and list of document parents
    """
    try:
        _id = ObjectId(_id)
    except bson.errors.InvalidId:
        return InvalidId()

    text = await Text(db, _id=_id).load()

    if not text.data:
        return NothingFound()

    return Ok(make_doc(text.id, text.data.text, await get_parents(db, _obj=text)))


def make_doc(_id: str or ObjectId, text: str, parents: list) -> dict:
    return dict(id=str(_id), text=text, parents=parents)


async def get_parents(db: motor_asyncio.AsyncIOMotorDatabase, _id: str or ObjectId = None, _obj: Text = None) -> list:
    seq = []

    if _id:
        text = await Text(db, _id=_id).load()
    elif _obj:
        text = _obj
    else:
        return seq

    while True:
        if text.data.parent != text.id:
            seq.append(str(text.data.parent))
        else:
            return seq

        text = await text.parent

        if not text.data:
            return seq

