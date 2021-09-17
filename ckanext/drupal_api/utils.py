from __future__ import annotations
import json
import pickle

from functools import wraps
from typing import Callable, Dict, Generic, Optional, TypeVar, Union, cast, Iterable

import requests

import ckan.plugins.toolkit as tk
import ckan.lib.redis as redis


CONFIG_DRUPAL_URL = "ckanext.drupal_api.instance.{name}.url"
CONFIG_DRUPAL_URL_DEFAULT = "ckanext.drupal_api.instance.url"

CONFIG_CACHE_DURATION = "ckanext.drupal_api.cache.duration"
CONFIG_REQUEST_TIMEOUT = "ckanext.drupal_api.timeout"

CONFIG_DRUPAL_API_VERSION = "ckanext.drupal_api.api_version"
JSON_API = "json"
CORE_API = "core"

DEFAULT_REQUEST_TIMEOUT = 5
DEFAULT_CACHE_DURATION = 3600

T = TypeVar("T")


class DontCache(Generic[T]):
    __slots__ = ("value",)
    value: T

    def __init__(self, value: T):
        self.value = value

    def unwrap(self) -> T:
        return self.value


Menu = Iterable[Dict]
MaybeNotCached = Union[T, DontCache[T]]


class Drupal:
    url: str

    @classmethod
    def get(cls, instance: str = "default") -> Drupal:
        # url = (
        #     tk.config.get(CONFIG_DRUPAL_URL.format(name=instance))
        #     or tk.config[CONFIG_DRUPAL_URL]
        # )
        url = tk.config.get(CONFIG_DRUPAL_URL_DEFAULT)
        return cls(url)

    def __init__(self, url: str):
        self.url = url.strip("/")
        self.timeout = tk.asint(
            tk.config.get(CONFIG_REQUEST_TIMEOUT, DEFAULT_REQUEST_TIMEOUT)
        )

    def full_url(self, path: str):
        return self.url + "/" + path.lstrip("/")


class JsonAPI(Drupal):
    def _request(self, entity_type: str, entity_name: str) -> Dict:
        url = self.url + f"/jsonapi/{entity_type}/{entity_name}"

        req = requests.get(url, timeout=self.timeout)
        req.raise_for_status()
        return req.json()

    def get_menu(self, name: str) -> MaybeNotCached[Menu]:
        data: dict = self._request("menu_items", name)

        details = {item["id"]: item["attributes"] for item in data["data"]}
        for v in sorted(details.values(), key=lambda v: v["weight"], reverse=True):
            v.setdefault("submenu", [])
            if v["url"].startswith("/"):
                v["url"] = self.full_url(v["url"])
            if v["parent"]:
                details[v["parent"]].setdefault("submenu", []).append(v)

        return [
            {"url": link["url"], "title": link["title"], "submenu": link["submenu"]}
            for link in details.values()
            if not link["parent"] and link["enabled"]
        ]


class CoreAPI(Drupal):
    def _request(self, endpoint: str) -> Dict:
        url = self.url + f"/resource/layout/export"

        req = requests.get(url, timeout=self.timeout)
        req.raise_for_status()
        return req.json()

    def get_menu(self, name: str) -> MaybeNotCached[Menu]:
        data = self._request(endpoint="/resource/layout/export")

        if not data:
            return {}

        return data.get(name, {})


def _get_api_version() -> Optional[Union[CoreAPI, JsonAPI]]:
    """
    Returns a connector class for an API
    There are two supported versions:
        - JSON API
        - Rest API (Drupal core)
    """
    supported_api = {JSON_API: JsonAPI, CORE_API: CoreAPI}

    api_version: str = tk.config.get(CONFIG_DRUPAL_API_VERSION)
    return supported_api.get(api_version)


def cached(func: Callable[..., MaybeNotCached[T]]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = _get_redis_conn()

        key = key_for(func.__name__) + pickle.dumps((args, kwargs))
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


def key_for(name: str) -> bytes:
    return bytes("ckan:" + tk.config["ckan.site_id"] + ":drupal-api:" + name, "utf8")


def drop_cache_for(name):
    import ipdb

    ipdb.set_trace()

    conn = _get_redis_conn()
    prefix = key_for(name)
    for k in conn.keys(prefix + b"*"):
        conn.delete(k)


def _get_redis_conn():
    return redis.connect_to_redis()
