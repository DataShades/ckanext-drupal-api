from __future__ import annotations

import ckan.types as types
import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.drupal_api.helpers as helpers


@tk.blanket.blueprints
class DrupalApiPlugin(p.SingletonPlugin):
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)
    p.implements(p.ISignal)

    # ITemplateHelpers

    def get_helpers(self):
        return helpers.get_helpers()

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")

    # ISignal

    def get_signal_subscriptions(self) -> types.SignalMapping:
        return {
            tk.signals.ckanext.signal("ap_main:collect_config_sections"): [
                self.collect_config_sections_subs
            ],
            tk.signals.ckanext.signal("ap_main:collect_config_schemas"): [
                self.collect_config_schemas_subs
            ],
        }

    @staticmethod
    def collect_config_sections_subs(sender: None):
        return {
            "name": "Drupal API",
            "configs": [
                {
                    "name": "Configuration",
                    "blueprint": "drupal_api.config",
                    "info": "Drupal API settings",
                },
            ],
        }

    @staticmethod
    def collect_config_schemas_subs(sender: None):
        return ["ckanext.drupal_api:config_schema.yaml"]


if tk.check_ckan_version("2.10"):
    tk.blanket.config_declarations(DrupalApiPlugin)
