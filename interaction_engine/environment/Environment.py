from environment.SetupFlag import setup_flag

class Environment:
    def __init__(self, ansible_runner, openstack_conn):
        self.ansible_runner = ansible_runner
        self.openstack_conn = openstack_conn
        self.ssh_key_path = './environment/ssh_keys/'

        self.flags = {}

    def check_flag(self, flag):
        if flag in self.flags:
            return self.flags[flag]
        return 0