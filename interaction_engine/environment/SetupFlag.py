import random
import string


def setup_flag(ansible_runner, host, path):
    # Generate flag
    flag = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))

    # Add flag to the host
    params = {'host': host, 'flag_path': path, 'flag_contents': flag}
    ansible_runner.run_playbook('goals/addFlag.yml', playbook_params=params)

    return flag