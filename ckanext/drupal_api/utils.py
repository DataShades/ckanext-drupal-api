from __future__ import annotations
import json
import pickle

from functools import wraps
from typing import Callable, Dict, Generic, TypeVar, Union, cast

import requests

import ckan.plugins.toolkit as tk
import ckan.lib.redis as redis

CONFIG_DRUPAL_URL = "ckanext.drupal_api.instance.{name}.url"
CONFIG_DRUPAL_URL_DEFAULT = "ckanext.drupal_api.instance.url"

CONFIG_CACHE_DURATION = "ckanext.drupal_api.cache.duration"
CONFIG_REQUEST_TIMEOUT = "ckanext.drupal_api.timeout"

DEFAULT_REQUEST_TIMEOUT = 5
DEFAULT_CACHE_DURATION = 3600

T = TypeVar('T')

class DontCache(Generic[T]):
    __slots__ = ('value',)
    value: T

    def __init__(self, value: T):
        self.value = value

    def unwrap(self) -> T:
        return self.value

MaybeNotCached = Union[T, DontCache[T]]


class Drupal:
    url: str

    @classmethod
    def get(cls, instance: str = "default") -> Drupal:
        url = (
            tk.config.get(CONFIG_DRUPAL_URL.format(name=instance))
            or tk.config[CONFIG_DRUPAL_URL]
        )
        return cls(url)

    def __init__(self, url: str):
        self.url = url.strip("/")

    def _request(self, entity_type: str, entity_name: str)->Dict:
        url = self.url + f"/jsonapi/{entity_type}/{entity_name}"
        timeout = tk.asint(
            tk.config.get(CONFIG_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT)
        )
        req = requests.get(url, timeout=timeout)
        req.raise_for_status()
        return req.json()

    def full_url(self, path: str):
        return self.url + '/' + path.lstrip('/')

    def get_menu(self, name: str) -> dict:
        return self._request("menu_items", name)


def cached(func: Callable[..., MaybeNotCached[T]]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = redis.connect_to_redis()

        key = pickle.dumps((args, kwargs))
        value = conn.get(key)
        if value:
            return cast(T, json.loads(value))

        value = func(*args, **kwargs)
        cache_duration = tk.asint(
            tk.config.get(CONFIG_CACHE_DURATION, DEFAULT_CACHE_DURATION)
        )
        if isinstance(value, DontCache):
            value = cast(T, value.unwrap())
        conn.set(key, json.dumps(value), ex=cache_duration)
        return value

    return wrapper
