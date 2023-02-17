class DefenderAction():

    def __init__(self, ansible_runner, openstack_conn):
        self.ansible_runner = ansible_runner
        self.openstack_conn = openstack_conn
        return
    
    def run(self):
        return