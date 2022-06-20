import ansible_runner
import openstackAPI

def main():
    conn = openstackAPI.initialize()
    manage_server, manage_ip = openstackAPI.find_manage_server(conn)
    ansible_vars = {'manage_ip': manage_ip}

    r = ansible_runner.run(extravars=ansible_vars, private_data_dir='../ansible/cage/', playbook='testPlaybook.yml')

    print("{}: {}".format(r.status, r.rc))

if __name__=="__main__":
    main()