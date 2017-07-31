from smsurvey.core.model.survey.owner import Owner

class Plugin:

    def __init__(self, plugin_id, owner_name, owner_domain, token, salt, permissions, poke_url):
        self.plugin_id = plugin_id
        self.owner_name = owner_name
        self.owner_domain = owner_domain
        self.token = token
        self.salt = salt
        self.permissions = permissions
        self.poke_url = poke_url

    @classmethod
    def from_tuple(cls, plugin_tuple):
        return cls(plugin_tuple[0], plugin_tuple[1], plugin_tuple[2], plugin_tuple[3], plugin_tuple[4],
                   plugin_tuple[5], plugin_tuple[6])
