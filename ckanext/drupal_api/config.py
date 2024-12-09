from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk


CONFIG_DRUPAL_URL = "ckanext.drupal_api.drupal_url"
DEFAULT_DRUPAL_URL = ""

CONFIG_CACHE_DURATION = "ckanext.drupal_api.cache.duration"
DEFAULT_CACHE_DURATION = 3600

CONFIG_REQUEST_TIMEOUT = "ckanext.drupal_api.timeout"
DEFAULT_REQUEST_TIMEOUT = 5

CONFIG_REQUEST_HTTP_USER = "ckanext.drupal_api.request.user"
CONFIG_REQUEST_HTTP_PASS = "ckanext.drupal_api.request.pass"

CONFIG_REQUEST_HTTP_HEADER_KEY = "ckanext.drupal_api.request.header.key"
CONFIG_REQUEST_HTTP_HEADER_VALUE = "ckanext.drupal_api.request.header.value"
DEFAULT_REQUEST_HEADER_KEY = "X-CKAN-API-Key"

CONFIG_DRUPAL_API_VERSION = "ckanext.drupal_api.api_version"
JSON_API = "json"
CORE_API = "core"
DEFAULT_API_VERSION = CORE_API


CONFIG_MENU_EXPORT = "ckanext.drupal_api.core.menu_export_endpoint"
DEFAULT_MENU_EXPORT_EP = "/resource/layout/export"


def get_cache_ttl() -> int:
    return tk.asint(tk.config[CONFIG_CACHE_DURATION] or DEFAULT_CACHE_DURATION)


def get_drupal_url() -> str:
    return (tk.config[CONFIG_DRUPAL_URL] or DEFAULT_DRUPAL_URL).strip("/")


def get_api_version() -> str:
    return tk.config[CONFIG_DRUPAL_API_VERSION] or DEFAULT_API_VERSION


def get_menu_export_endpoint() -> str:
    if get_api_version() == JSON_API:
        return "/jsonapi/menu_items/{menu_id}"

    return tk.config[CONFIG_MENU_EXPORT] or DEFAULT_MENU_EXPORT_EP


def get_request_timeout() -> int:
    return tk.asint(tk.config[CONFIG_REQUEST_TIMEOUT] or DEFAULT_REQUEST_TIMEOUT)


def get_http_user() -> str | None:
    return tk.config[CONFIG_REQUEST_HTTP_USER]


def get_http_pass() -> str | None:
    return tk.config[CONFIG_REQUEST_HTTP_PASS]

def get_http_header_key() -> str:
    return tk.config[CONFIG_REQUEST_HTTP_HEADER_KEY] or DEFAULT_REQUEST_HEADER_KEY

def get_http_header_value() -> str | None:
    return tk.config[CONFIG_REQUEST_HTTP_HEADER_VALUE]

def get_config_options() -> dict[str, dict[str, Any]]:
    """Defines how we are going to render the global configuration
    options for an extension."""
    unicode_safe = tk.get_validator("unicode_safe")
    one_of = tk.get_validator("one_of")
    default = tk.get_validator("default")
    int_validator = tk.get_validator("is_positive_integer")
    url_validator = tk.get_validator("url_validator")

    return {
        "cache_ttl": {
            "key": CONFIG_CACHE_DURATION,
            "label": tk._("Cache TTL"),
            "value": get_cache_ttl(),
            "validators": [default(DEFAULT_CACHE_DURATION), int_validator],
            "type": "number",
        },
        "drupal_url": {
            "key": CONFIG_DRUPAL_URL,
            "label": tk._("Drupal base URL"),
            "value": get_drupal_url(),
            "validators": [unicode_safe, url_validator],
            "type": "text",
            "required": True,
        },
        "api_version": {
            "key": CONFIG_DRUPAL_API_VERSION,
            "label": tk._("API version"),
            "value": get_api_version(),
            "validators": [default(DEFAULT_API_VERSION), one_of([JSON_API, CORE_API])],
            "type": "select",
            "options": [
                {"value": JSON_API, "text": "JSON API"},
                {"value": CORE_API, "text": "Core REST API"},
            ],
        },
        "menu_export_endpoint": {
            "key": CONFIG_MENU_EXPORT,
            "label": tk._("Menu export API endpoint"),
            "value": get_menu_export_endpoint(),
            "validators": [unicode_safe],
            "type": "text",
            "disabled": get_api_version() == JSON_API,
            "required": True,
            "help_text": tk._(
                "If you are using the core API version, you might face the situation when your endpoint differ from the default one"
            ),
        },
        "request_timeout": {
            "key": CONFIG_REQUEST_TIMEOUT,
            "label": tk._("API request timeout"),
            "value": get_request_timeout(),
            "validators": [default(DEFAULT_REQUEST_TIMEOUT), int_validator],
            "type": "number",
        },
        "http_user": {
            "key": CONFIG_REQUEST_HTTP_USER,
            "label": tk._("HTTP auth user"),
            "value": get_http_user(),
            "validators": [unicode_safe],
            "type": "text",
        },
        "http_pass": {
            "key": CONFIG_REQUEST_HTTP_PASS,
            "label": tk._("HTTP auth password"),
            "value": get_http_pass(),
            "validators": [unicode_safe],
            "type": "password",
        },
        "http_header_key": {
            "key": CONFIG_REQUEST_HTTP_HEADER_KEY,
            "label": tk._("HTTP header auth key"),
            "value": get_http_header_key(),
            "validators": [default(DEFAULT_REQUEST_HEADER_KEY), unicode_safe],
            "type": "text",
        },
        "http_header_value": {
            "key": CONFIG_REQUEST_HTTP_HEADER_VALUE,
            "label": tk._("HTTP header auth key value"),
            "value": get_http_header_value(),
            "validators": [unicode_safe],
            "type": "password",
        },
    }
