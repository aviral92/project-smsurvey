import json
import os
import time
from base64 import b64encode

import requests

from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where

from smsurvey.core.security import secure
from smsurvey.core.services.owner_service import OwnerService


class PluginService:

    @staticmethod
    def get_plugin(plugin_id):
        plugins = Model.repository.plugins
        return plugins.select(Where(plugins.id, Where.EQUAL, plugin_id))

    @staticmethod
    def validate_plugin(plugin_id, owner_name, owner_domain, token):
        plugin = PluginService.get_plugin(plugin_id)

        if plugin is not None:
            owner = OwnerService.get_by_id(plugin.owner_id)
            if owner_name == owner.name and owner_domain == owner.domain:
                test = secure.encrypt_password(token, plugin.salt).decode()
                return test == plugin.secret_token

        return False

    @staticmethod
    def is_plugin_registered(plugin_id):
        return PluginService.get_plugin(plugin_id) is not None

    @staticmethod
    def register_plugin(owner_name, owner_domain, owner_password, poke_url, permissions):
        if OwnerService.does_owner_exist(owner_name, owner_domain):
            if OwnerService.validate_password(owner_name, owner_domain, owner_password):

                owner_id = OwnerService.get_owner_id(owner_name, owner_domain)
                token = secure.encrypt_password(owner_domain + owner_name + str(time.time())).decode()
                salt_for_token = b64encode(os.urandom(16)).decode()
                salted_token = secure.encrypt_password(token, salt_for_token).decode()

                plugins = Model.repository.plugins
                plugin = plugins.create()

                plugin.owner_id = owner_id
                plugin.secret_token = salted_token
                plugin.salt = salt_for_token
                plugin.permissions = permissions
                plugin.poke_url = poke_url

                return plugin.save(), token

    @staticmethod
    def poke(plugin_id, survey_id):
        plugin = PluginService.get_plugin(plugin_id)

        data = {
            'plugin_id': plugin_id,
            'survey_id': survey_id
        }

        requests.post(plugin.poke_url, json.dumps(data))