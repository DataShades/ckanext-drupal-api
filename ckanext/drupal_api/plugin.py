import ckan.plugins as p
import ckan.plugins.toolkit as tk

import ckanext.drupal_api.helpers as helpers
from ckanext.drupal_api.views import blueprints

class DrupalApiPlugin(p.SingletonPlugin):
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurer)
    p.implements(p.IBlueprint)

    # ITemplateHelpers

    def get_helpers(self):
        return helpers.get_helpers()

    # IConfigurer

    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")
        tk.add_ckan_admin_tab(config_, "drupal_api.drupal_api_config", "Drupal API")

    # IBlueprint

    def get_blueprint(self):
        return blueprints