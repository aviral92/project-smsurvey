import json
import os
import time
import re
import requests

from base64 import b64encode


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
    def get_by_owner_id(owner_id):
        plugins = Model.repository.plugins
        return plugins.select(Where(plugins.owner_id, Where.E, owner_id), force_list=True)

    @staticmethod
    def validate_plugin(plugin_id, owner_id, token):
        plugin = PluginService.get_plugin(plugin_id)
        owner = OwnerService.get_by_id(owner_id)

        if plugin and owner is not None:
            if plugin.owner_id == owner.id:
                test = secure.encrypt_password(token, plugin.salt).decode()
                return test == plugin.secret_token

        return False

    @staticmethod
    def is_owned_by(plugin_id, owner_id):
        plugin = PluginService.get_plugin(plugin_id)

        if plugin is None:
            return False

        return plugin.owner_id == owner_id

    @staticmethod
    def is_plugin_registered(plugin_id):
        return PluginService.get_plugin(plugin_id) is not None

    @staticmethod
    def register_plugin(name, owner_id, url, icon, permissions):

        token = secure.encrypt_password(str(owner_id) + str(time.time())).decode()
        salt_for_token = b64encode(os.urandom(16)).decode()
        salted_token = secure.encrypt_password(token, salt_for_token).decode()

        plugins = Model.repository.plugins
        plugin = plugins.create()

        plugin.name = name
        plugin.owner_id = owner_id
        plugin.secret_token = salted_token
        plugin.salt = salt_for_token
        plugin.permissions = permissions
        plugin.icon = icon
        plugin.url = url

        return plugin.save(), token

    @staticmethod
    def delete_plugin(plugin_id):
        plugins = Model.repository.plugins
        plugins.delete(Where(plugins.id, Where.E, plugin_id))

    @staticmethod
    def poke(plugin_id, survey_id):
        print("Printing plugin ID", plugin_id)
        plugin = PluginService.get_plugin(plugin_id)
        print("Getting Plugin", plugin)
        data = {
            'plugin_id': plugin_id,
            'survey_id': survey_id
        }
        print("Data Plugin", data)
        requests.post(plugin.url + "/poke/", json.dumps(data))

    @staticmethod
    def send_message(plugin_id, instance_id, message):
        plugin = PluginService.get_plugin(plugin_id)

        data = {
            'plugin_id': plugin_id,
            'instance_id': instance_id,
            'message': message
        }

        requests.post(plugin.url + '/message/', json.dumps(data))

    @staticmethod
    def get_plugins_with_at_least_permissions(permissions):
        # This will not scale

        permissions_regex = ""
        for char in permissions:
            if char == '1':
                permissions_regex += '[1|2|3|4]'
            elif char == '2':
                permissions_regex += '[2|4]'
            elif char == '3':
                permissions_regex += '[3|4]'
            else:
                permissions_regex += char

        plugins = Model.repository.plugins.select(force_list=True)

        matched = []
        for plugin in plugins:
            if re.match(permissions_regex, plugin.permissions):
                matched.append(plugin)

        return matched

