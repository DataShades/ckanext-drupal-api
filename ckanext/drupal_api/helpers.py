from typing import Callable, Dict, Iterable

from ckanext.drupal_api.utils import Drupal, cached


_helpers: Dict[str, Callable] = {}


def helper(func: Callable):
    _helpers[f"drupal_api_{func.__name__}"] = func
    return func


def get_helpers():
    return dict(_helpers)


@helper
@cached
def menu(name: str, with_disabled: bool = False) -> Iterable:
    drupal = Drupal.get()
    data = drupal.get_menu(name)

    details = {
        item['id']: item['attributes']
        for item in data['data']
    }
    for v in sorted(details.values(), key=lambda v: v['weight'], reverse=True):
        if v['parent']:
            details[v['parent']].setdefault('submenu', []).append(v)

    return [
        {
            'url': link['url'],
            'title': link['title'],
            'submenu': link.get('submenu', []),
        }
        for link in details.values()
        if not link['parent'] and (with_disabled or link['enabled'])
    ]
