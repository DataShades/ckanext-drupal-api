import logging

from flask import Blueprint

import ckan.plugins as p
import ckan.plugins.toolkit as tk

from ckanext.drupal_api.helpers import custom_endpoint, menu
from ckanext.drupal_api.utils import drop_cache_for

log = logging.getLogger(__name__)
drupal_api = Blueprint("drupal_api", __name__)


def ap_before_request() -> None:
    try:
        tk.check_access("sysadmin", {"user": tk.current_user.name})
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


drupal_api.before_request(ap_before_request)

if p.plugin_loaded("admin_panel"):
    from ckanext.ap_main.views.generics import ApConfigurationPageView

    @drupal_api.route("/drupal_api/clear_cache", methods=["POST"])
    def clear_cache() -> str:
        if "clear-menu-cache" in tk.request.form:
            drop_cache_for(menu.__name__)

        if "clear-custom-cache" in tk.request.form:
            drop_cache_for(custom_endpoint.__name__)

        tk.h.flash_success(tk._("Cache has been cleared"))

        return tk.h.redirect_to("drupal_api.config")

    drupal_api.add_url_rule(
        "/drupal_api/config",
        view_func=ApConfigurationPageView.as_view(
            "config",
            "drupal_api_config",
            render_template="drupal_api/config.html",
            page_title=tk._("Drupal API config"),
        ),
    )
