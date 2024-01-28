from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.drupal_api.helpers as helpers
from ckanext.drupal_api.views import blueprints

import ckanext.ap_main.types as ap_types
from ckanext.ap_main.interfaces import IAdminPanel


class DrupalApiPlugin(p.SingletonPlugin):
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(IAdminPanel, inherit=True)

    # ITemplateHelpers

    def get_helpers(self):
        return helpers.get_helpers()

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")

    # IBlueprint

    def get_blueprint(self):
        return blueprints

    # IAdminPanel

    def register_config_sections(
        self, config_list: list[ap_types.SectionConfig]
    ) -> list[ap_types.SectionConfig]:
        config_list.append(
            ap_types.SectionConfig(
                name="Drupal API",
                configs=[
                    ap_types.ConfigurationItem(
                        name="Configuration",
                        blueprint="drupal_api.config",
                        info="Drupal API settings",
                    )
                ],
            )
        )
        return config_list


if tk.check_ckan_version("2.10"):
    tk.blanket.config_declarations(DrupalApiPlugin)
