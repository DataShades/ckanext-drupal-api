import logging

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.ap_main.utils import ap_before_request
from ckanext.ap_main.views.generics import ApConfigurationPageView

import ckanext.drupal_api.config as da_conf
from ckanext.drupal_api.utils import drop_cache_for
from ckanext.drupal_api.helpers import custom_endpoint, menu


log = logging.getLogger(__name__)
drupal_api = Blueprint("drupal_api", __name__, url_prefix="/admin-panel/drupal_api")
drupal_api.before_request(ap_before_request)


class ConfigClearCacheView(MethodView):
    def post(self):
        if "clear-menu-cache" in tk.request.form:
            drop_cache_for(menu.__name__)

        if "clear-custom-cache" in tk.request.form:
            drop_cache_for(custom_endpoint.__name__)

        tk.h.flash_success(tk._("Cache has been cleared"))

        return tk.h.redirect_to("drupal_api.config")


drupal_api.add_url_rule(
    "/config",
    view_func=ApConfigurationPageView.as_view(
        "config",
        "drupal_api_config",
        render_template="drupal_api/config.html",
        page_title=tk._("Drupal API config")
    )
)
drupal_api.add_url_rule(
    "/clear_cache",
    view_func=ConfigClearCacheView.as_view("clear_cache"),
    methods=("POST",),
)

blueprints = [drupal_api]
