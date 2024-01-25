import logging

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan.logic import parse_params

from ckanext.ap_main.utils import ap_before_request

import ckanext.drupal_api.config as da_conf
from ckanext.drupal_api.utils import drop_cache_for
from ckanext.drupal_api.helpers import custom_endpoint, menu


log = logging.getLogger(__name__)
drupal_api = Blueprint("drupal_api", __name__, url_prefix="/admin-panel/drupal_api")
drupal_api.before_request(ap_before_request)


class ConfigView(MethodView):
    def get(self):
        return tk.render(
            "drupal_api/config.html",
            {"configs": da_conf.get_config_options(), "data": {}, "errors": {}},
        )

    def post(self):
        data_dict = parse_params(tk.request.form)

        try:
            tk.get_action("config_option_update")(
                {"user": tk.current_user.name},
                data_dict,
            )
        except tk.ValidationError as e:
            return tk.render(
                "drupal_api/config.html",
                extra_vars={
                    "data": data_dict,
                    "errors": e.error_dict,
                    "error_summary": e.error_summary,
                    "configs": da_conf.get_config_options(),
                },
            )

        tk.h.flash_success(tk._("Config options have been updated"))
        return tk.h.redirect_to("drupal_api.config")


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
    view_func=ConfigView.as_view("config"),
    methods=("GET", "POST"),
)
drupal_api.add_url_rule(
    "/clear_cache",
    view_func=ConfigClearCacheView.as_view("clear_cache"),
    methods=("POST",),
)

blueprints = [drupal_api]
