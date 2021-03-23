import logging
from typing import Callable, Dict, Iterable, TypeVar

from requests.exceptions import HTTPError, ConnectTimeout

from ckanext.drupal_api.utils import Drupal, cached, DontCache, MaybeNotCached


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
def menu(name: str, with_disabled: bool = False) -> MaybeNotCached[Menu]:
    drupal = Drupal.get()
    try:
        data = drupal.get_menu(name)
    except (HTTPError, ConnectTimeout) as e:
        log.error('Cannot get drupal menu %s: %s', name, e)
        return DontCache([])
    details = {
        item['id']: item['attributes']
        for item in data['data']
    }
    for v in sorted(details.values(), key=lambda v: v['weight'], reverse=True):
        v.setdefault('submenu', [])
        if v['url'].startswith('/'):
            v['url'] = drupal.full_url(v['url'])
        if v['parent']:
            details[v['parent']].setdefault('submenu', []).append(v)

    return [
        {
            'url': link['url'],
            'title': link['title'],
            'submenu': link['submenu']
        }
        for link in details.values()
        if not link['parent'] and (with_disabled or link['enabled'])
    ]
