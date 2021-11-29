from __future__ import annotations
import logging
from typing import Optional
from urllib.parse import urljoin
import requests

import ckan.plugins.toolkit as tk

import ckanext.drupal_api.config as c


log = logging.getLogger(__name__)


class Drupal:
    url: str

    @classmethod
    def get(cls, instance: str = "default") -> Optional[Drupal]:
        url = tk.config.get(c.CONFIG_DRUPAL_URL)
        if not url:
            log.error("Drupal URL is missing: %s", c.CONFIG_DRUPAL_URL)
            return
        default_lang = tk.config.get("ckan.locale_default")
        current_lang = tk.h.lang()
        localised_url = url.format(LANG=current_lang if current_lang != default_lang else "")
        return cls(localised_url)

    def __init__(self, url: str):
        self.url = url.strip("/")
        self.timeout = tk.asint(
            tk.config.get(c.CONFIG_REQUEST_TIMEOUT, c.DEFAULT_REQUEST_TIMEOUT)
        )

    def full_url(self, path: str):
        return urljoin(self.url, path)


class JsonAPI(Drupal):
    def _request(self, entity_type: str, entity_name: str) -> dict:
        url = self.url + f"/jsonapi/{entity_type}/{entity_name}"

        http_user: str = tk.config.get(c.CONFIG_REQUEST_HTTP_USER)
        http_pass: str = tk.config.get(c.CONFIG_REQUEST_HTTP_PASS)

        session = requests.Session()

        if http_user and http_pass:
            session.auth = (http_user, http_pass)

        req = session.get(url, timeout=self.timeout, verify=False)
        req.raise_for_status()
        return req.json()

    def get_menu(self, name: str) -> list[dict[str, str]]:
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

        http_user: str = tk.config.get(c.CONFIG_REQUEST_HTTP_USER)
        http_pass: str = tk.config.get(c.CONFIG_REQUEST_HTTP_PASS)

        session = requests.Session()

        if http_user and http_pass:
            session.auth = (http_user, http_pass)

        req = session.get(url, timeout=self.timeout)
        req.raise_for_status()
        return req.json()

    def get_menu(self, name: str) -> dict:
        data: dict = self._request(
            endpoint=tk.config.get(c.CONFIG_MENU_EXPORT, c.DEFAULT_MENU_EXPORT_EP)
        )
        log.info(
            f"Menu {name} has been fetched successfully. Cached for \
                {tk.config.get(c.CONFIG_CACHE_DURATION, c.DEFAULT_CACHE_DURATION)} seconds"
        )
        return data.get(name, {})
