import ansible_runner
import argparse
import openstackAPI


def main(args):
    conn = openstackAPI.initialize()
    manage_server, manage_ip = openstackAPI.find_manage_server(conn)
    ansible_vars = {'manage_ip': manage_ip, 'ssh_key_path': args.ssh_key_path}

    r = ansible_runner.run(extravars=ansible_vars, private_data_dir='../ansible/cage/', playbook='testPlaybook.yml')

    print("{}: {}".format(r.status, r.rc))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ssh_key_path', help='The path to your openstack ssh key')
    args = parser.parse_args()

    main(args)
