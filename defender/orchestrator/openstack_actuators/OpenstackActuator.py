class OpenstackActuator:

    def __init__(self, openstack_conn, ansible_runner):
        self.openstack_conn = openstack_conn
        self.ansible_runner = ansible_runner
        return
    
    # Subclass overwrites to run action
    def actuate(self, action):
        return