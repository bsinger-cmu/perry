from .Arsenal import Arsenal


class CountArsenal(Arsenal):
    def __init__(self, arsenal_data):
        self.storage = arsenal_data["storage"]
        return

    # Define by subclass
    def get_capabilities(self):
        return self.storage.keys()

    def get_max_capability_count(self, capability):
        return self.storage[capability]

    # Define by subclass
    def update_storage(self, action):
        return
