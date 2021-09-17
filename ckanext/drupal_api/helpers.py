import logging
from typing import Callable, Dict, Iterable, TypeVar

from requests.exceptions import HTTPError, ConnectTimeout

from ckanext.drupal_api.utils import Drupal, cached, DontCache, MaybeNotCached, _get_api_version


_helpers: Dict[str, Callable] = {}
log = logging.getLogger(__name__)

T = TypeVar('T', bound=Callable)
Menu = Iterable[Dict]


def helper(func: T) -> T:
    _helpers[f"drupal_api_{func.__name__}"] = func
    return func


def get_helpers():
    return dict(_helpers)


@helper
@cached
def menu(name: str) -> MaybeNotCached[Menu]:
    api_connector = _get_api_version()
    
    if not api_connector:
        return DontCache([])

    drupal_api = api_connector.get()

    try:
        menu = drupal_api.get_menu(name)
    except (HTTPError, ConnectTimeout) as e:
        log.error(f'Request error during menu fetching - {name}: {e}')
        return DontCache([])

    return menu

