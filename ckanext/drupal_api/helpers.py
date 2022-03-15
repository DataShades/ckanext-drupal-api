from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional
from urllib.parse import urljoin

from requests.exceptions import RequestException

import ckan.plugins.toolkit as tk

import ckanext.drupal_api.config as c
from ckanext.drupal_api.utils import cached, _get_api_version
from ckanext.drupal_api.logic.api import make_request
from ckanext.drupal_api.types import Menu, T, MaybeNotCached, DontCache


_helpers: Dict[str, Callable] = {}
log = logging.getLogger(__name__)


def helper(func: T) -> T:
    _helpers[f"drupal_api_{func.__name__}"] = func
    return func


def get_helpers():
    return dict(_helpers)


@helper
@cached
def menu(name: str, cache_extras: Optional[dict[str, Any]] = None) -> MaybeNotCached[Menu]:
    api_connector = _get_api_version()
    drupal_api = api_connector.get()

    if not drupal_api:
        return DontCache({})

    try:
        menu = drupal_api.get_menu(name)
    except RequestException as e:
        log.error(f"Request error during menu fetching - {name}: {e}")
        return DontCache({})

    return menu

@helper
@cached
def custom_endpoint(endpoint: str) -> dict:
    """Makes a request to the custom endpoint

    Args:
        endpoint (str): an endpoint URL part

    Returns:
        dict: response from Drupal
    """
    base_url = tk.config.get(c.CONFIG_DRUPAL_URL)
    if not base_url:
        log.error("Drupal URL is missing: %s", c.CONFIG_DRUPAL_URL)
        return
    
    try:
        resp = make_request(urljoin(base_url, endpoint))
    except RequestException as e:
        log.error(f"Custom endpoint request error - {endpoint}: {e}")
        return DontCache({})
    return resp
