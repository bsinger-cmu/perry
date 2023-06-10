from .Arsenal import Arsenal

class CountArsenal(Arsenal):

    def __init__(self, arsenal_data):
        self.storage = arsenal_data['storage']
        return

    # Define by subclass
    def get_capabilities(self):
        return self.storage.keys()

    # Define by subclass
    def update_storage(self, action):
        return