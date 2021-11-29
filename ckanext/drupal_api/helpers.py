import logging
from typing import Callable, Dict

from requests.exceptions import RequestException

from ckanext.drupal_api.utils import cached, _get_api_version
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
def menu(name: str, _cache_extra: str = "en") -> MaybeNotCached[Menu]:
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
