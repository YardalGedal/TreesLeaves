import json

from typing import Optional

__all__ = ['Result', 'Ok', 'Error', 'TextNotPassed', 'NothingFound', 'InvalidId']


class Result:
    TYPE: str = 'unknown'
    EXTRA: Optional[str, dict, list, tuple] = None

    def __init__(self, extra: Optional[str, dict, list, tuple] = None):
        self.extra = self.EXTRA or extra

    def __repr__(self) -> str:
        return json.dumps({self.TYPE: self.extra})


class Ok(Result):
    TYPE = 'ok'


class Error(Result):
    TYPE = 'error'


class TextNotPassed(Error):
    EXTRA = 'text not passed'


class NothingFound(Error):
    EXTRA = 'nothing found'


class InvalidId(Error):
    EXTRA = 'invalid id'
