from typing import Callable, Dict, Iterable

from ckanext.drupal_api.utils import Drupal, cached


_helpers: Dict[str, Callable] = {}


def helper(func: Callable):
    _helpers[f"drupal_api_{func.__name__}"] = func
    return func


def get_helpers():
    return dict(_helpers)


@cached
def menu(name: str, with_disabled: bool = False) -> Iterable:
    drupal = Drupal.get()
    data = drupal.get_menu(name)
    details = [
        item['attributes']
        for item in data['data']
    ]

    return [
        {
            'url': link['url'],
            'title': link['title']
        }
        for link in details
        if with_disabled or link['enabled']
    ]
