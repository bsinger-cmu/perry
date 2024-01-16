class Host:
    def __init__(self, name: str, ip: str, users: list[str] | None = None):
        self.name = name
        self.ip = ip

        if users is None:
            self.users = []
        else:
            self.users = users

    def add_user(self, user: str):
        self.users.append(user)
