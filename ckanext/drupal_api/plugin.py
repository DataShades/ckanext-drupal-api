import ckan.plugins as plugins

import ckanext.drupal_api.helpers as helpers


class DrupalApiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.ITemplateHelpers)

    # ITemplateHelpers

    def get_helpers(self):
        return helpers.get_helpers()
