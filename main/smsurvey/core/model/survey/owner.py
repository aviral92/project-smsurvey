
class Owner:

    def __init__(self, name, domain, password, salt):
        self.name = name
        self.domain = domain
        self.password = password
        self.salt = salt

    @classmethod
    def from_tuple(cls, owner_tuple):
        return cls(owner_tuple[0], owner_tuple[1], owner_tuple[2], owner_tuple[3])