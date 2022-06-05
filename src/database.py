from __future__ import annotations

from sys import platform

from typing import Generic, TypeVar, Protocol

from redis import Redis
from pickledb import PickleDB, load


class Hashable(Protocol):
    def __hash__(self) -> int:
        ...


T = TypeVar("T", bound=Hashable)


class Database(Generic[T]):
    """
    Class to represent a database.

    On windows, the database is a pickledb database.
    On linux, the database is a redis database.
    """
    def __init__(self):
        self.db: Redis | PickleDB
        if platform in ("linux", "linux2"):
            self.db = Redis(host="localhost", port=6379, db=0)
            self.db.flushdb()
        else:
            self.db = load("../database.db", True)

    def get_db(self) -> Redis | PickleDB:
        """
        Return an instance of the database.

        :return: a transparent interface to the underlying database object.
        """
        return self.db

    def get(self, key: str) -> T:
        """
        Get the value associated with a key.

        :param key: the key to get the value for
        :return: the value associated with the key
        """
        return self.db.get(key)

    def set(self, key: str, value: T) -> None:
        """
        Set the value associated with a key.

        :param key: the key to set the value for
        :param value: the value to set
        :return: None
        """
        self.db.set(key, value)

    def delete(self, key: str) -> None:
        """
        Delete a key.

        :param key: the key to delete
        :return: None
        """
        self.db.delete(key)

    def flush(self) -> None:
        """
        Flush the database

        :return: None
        """
        self.db.flushdb()
