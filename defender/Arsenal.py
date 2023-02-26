class Arsenal(object):

    def __init__(self):
        self.storage = {}

    # Define by subclass
    def get_capabilities(self):
        return []

    # Define by subclass
    def update_storage(self, action):
        return