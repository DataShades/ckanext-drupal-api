import logging

from flask import Blueprint

import ckan.plugins.toolkit as tk

from ckanext.drupal_api.utils import CONFIG_CACHE_DURATION, DEFAULT_CACHE_DURATION, drop_cache_for
from ckanext.drupal_api.helpers import menu


log = logging.getLogger(__name__)
drupal_api = Blueprint("drupal_api", __name__)


@drupal_api.route("/ckan-admin/drupal-api", methods=("GET", "POST"))
def manage_cache():
    """
    Invalidates cache
    """
    if not tk.request.form:
        return tk.render(
            "admin/manage_cache.html",
            {
                "cache_lifespan": tk.config.get(
                    CONFIG_CACHE_DURATION, DEFAULT_CACHE_DURATION
                )
            },
        )
    else:
        if "clear-menu-cache" in tk.request.form:
            drop_cache_for(menu.__name__)
            tk.h.flash_success(tk._("Cache has been cleared"))

        return tk.h.redirect_to("drupal_api.manage_cache")


blueprints = [drupal_api]
