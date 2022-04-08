import logging

from flask import Blueprint

import ckan.plugins.toolkit as tk
import ckan.model as model

import ckanext.drupal_api.config as c
from ckanext.drupal_api.utils import drop_cache_for, _get_menu_export_endpoint
from ckanext.drupal_api.helpers import custom_endpoint, menu


log = logging.getLogger(__name__)
drupal_api = Blueprint("drupal_api", __name__)



@drupal_api.before_request
def before_request():
    try:
        context = {
            "model": model,
            "user": tk.g.user,
            "auth_user_obj": tk.g.userobj
        }
        tk.check_access('sysadmin', context)
    except tk.NotAuthorized:
        tk.base.abort(403, tk._('Need to be system administrator to manage cache'))


@drupal_api.route("/ckan-admin/drupal-api", methods=("GET", "POST"))
def drupal_api_config():
    """
    Invalidates cache
    """
    if not tk.request.form:
        return tk.render(
            "admin/drupal_api_config.html",
            {
                "cache_ttl_default": c.DEFAULT_CACHE_DURATION,
                "cache_ttl_current": tk.config.get(c.CONFIG_CACHE_DURATION),
                "drupal_url": tk.config.get(c.CONFIG_DRUPAL_URL, "").strip('/'),
                "menu_export_endpoint": _get_menu_export_endpoint(),
                "api_version": tk.config.get(c.CONFIG_DRUPAL_API_VERSION, c.DEFAULT_API_VERSION)
            },
        )
    else:
        if "clear-menu-cache" in tk.request.form:
            drop_cache_for(menu.__name__)
            tk.h.flash_success(tk._("Cache has been cleared"))

        if "clear-custom-cache" in tk.request.form:
            drop_cache_for(custom_endpoint.__name__)

        return tk.h.redirect_to("drupal_api.drupal_api_config")


blueprints = [drupal_api]
