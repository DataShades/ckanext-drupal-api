from __future__ import annotations
import logging
import json
import pickle

from functools import wraps
from typing import Callable, Dict, Optional, Union, cast, Any


import ckan.plugins.toolkit as tk
import ckan.lib.redis as redis

import ckanext.drupal_api.config as c
from ckanext.drupal_api.types import T, MaybeNotCached, DontCache
from ckanext.drupal_api.logic.api import CoreAPI, JsonAPI

log = logging.getLogger(__name__)


def _get_api_version() -> Optional[Union[CoreAPI, JsonAPI]]:
    """
    Returns a connector class for an API
    There are two supported versions:
        - JSON API
        - Rest API (Drupal core)
    """
    supported_api = {c.JSON_API: JsonAPI, c.CORE_API: CoreAPI}

    api_version: str = tk.config.get(c.CONFIG_DRUPAL_API_VERSION, c.DEFAULT_API_VERSION)
    return supported_api.get(api_version)


def cached(func: Callable[..., MaybeNotCached[T]]) -> Callable[..., T]:
    """
    Caches function result into redis

    The key is a prefix from `key_for` function and a pickled args
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = _get_redis_conn()

        key = key_for(func.__name__) + pickle.dumps((args, kwargs))
        value = conn.get(key)
        if value:
            return cast(T, json.loads(value))

        value = func(*args, **kwargs)
        cache_duration = tk.asint(
            tk.config.get(c.CONFIG_CACHE_DURATION, c.DEFAULT_CACHE_DURATION)
        )

        if isinstance(value, DontCache):
            return cast(T, value.unwrap())
        conn.set(key, json.dumps(value), ex=cache_duration)
        return value

    return wrapper


def key_for(name: str) -> bytes:
    """
    Generates a unique prefix for redis by uniting
    ckan site_id, extension name and function name
    """
    return bytes("ckan:" + tk.config["ckan.site_id"] + ":drupal-api:" + name, "utf8")


def drop_cache_for(name):
    """
    Deletes keys from redis with the specified prefix
    """
    conn = _get_redis_conn()
    prefix = key_for(name)
    for k in conn.keys(prefix + b"*"):
        conn.delete(k)


def _get_redis_conn():
    return redis.connect_to_redis()


def _get_menu_export_endpoint():
    if tk.config.get(
        c.CONFIG_DRUPAL_API_VERSION, c.DEFAULT_API_VERSION
    ) == "json":
        return "/jsonapi/menu_items/{menu_id}"
    else:
        tk.config.get(c.CONFIG_MENU_EXPORT, c.DEFAULT_MENU_EXPORT_EP)