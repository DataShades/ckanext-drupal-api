from __future__ import annotations

import logging
import requests
from typing import Optional
from urllib.parse import urljoin

import ckan.plugins.toolkit as tk
import ckan.plugins as p

import ckanext.drupal_api.config as da_conf


log = logging.getLogger(__name__)


def make_request(url: str) -> dict:
    http_user = da_conf.get_http_user()
    http_pass = da_conf.get_http_pass()
    http_header_key = da_conf.get_http_header_key()
    http_header_value = da_conf.get_http_header_value()
    timeout = da_conf.get_request_timeout()

    session = requests.Session()

    if http_user and http_pass:
        session.auth = (http_user, http_pass)
    if http_header_key and http_header_value:
        session.headers[http_header_key] = http_header_value

    _add_drupal_session(session)
    req = session.get(url, timeout=timeout)
    req.raise_for_status()
    return req.json()


class Drupal:
    url: str

    @classmethod
    def get(cls, instance: str = "default") -> Optional[Drupal]:
        url = da_conf.get_drupal_url()

        if not url:
            log.error("Drupal URL is missing: %s", da_conf.CONFIG_DRUPAL_URL)
            return

        default_lang = tk.config.get("ckan.locale_default")
        current_lang = tk.h.lang()
        localised_url = url.format(
            LANG=current_lang if current_lang != default_lang else ""
        )
        return cls(localised_url)

    def __init__(self, url: str):
        self.url = url.strip("/")

    def full_url(self, path: str):
        return urljoin(self.url, path)


class JsonAPI(Drupal):
    def _request(self, entity_type: str, entity_name: str) -> dict:
        url = self.url + f"/jsonapi/{entity_type}/{entity_name}"
        return make_request(url)

    def get_menu(self, name: str) -> list[dict[str, str]]:
        data: dict = self._request("menu_items", name)

        details = {item["id"]: item["attributes"] for item in data["data"]}
        for v in sorted(details.values(), key=lambda v: v["weight"], reverse=True):
            v.setdefault("submenu", [])
            if v["url"].startswith("/"):
                v["url"] = self.full_url(v["url"])
            if v["parent"]:
                if v["parent"] not in details:
                    continue
                details[v["parent"]].setdefault("submenu", []).append(v)
        return [
            link for link in details.values() if not link["parent"] and link["enabled"]
        ]


class CoreAPI(Drupal):
    """
    The core Rest API modules doesn't provide endpoints by default

    So every endpoint is our custom one. E.g `/resource/layout/export`
    on the first portal could be `/layout/resource/export` on the another one.

    This is a huge problem that prevents us from unifying requests.
    In this case, the reliable solution is to provide a possibility
    to configure every endpoint.
    """

    def _request(self, endpoint: str) -> dict:
        url = self.url + endpoint
        return make_request(url)

    def get_menu(self, name: str) -> dict:
        data: dict = self._request(endpoint=da_conf.get_menu_export_endpoint())
        log.info(
            f"Menu {name} has been fetched successfully. Cached for \
                {da_conf.get_cache_ttl()} seconds"
        )
        return data.get(name, {})


def _add_drupal_session(session: requests.Session):
    if not tk.request or not p.plugin_loaded("drupal_idp"):
        return

    try:
        from ckanext.drupal_idp.utils import session_cookie_name
    except ImportError:
        return

    name = session_cookie_name()
    sid = tk.request.cookies.get(name)
    if sid:
        session.headers["Cookie"] = f"{name}={sid}"
