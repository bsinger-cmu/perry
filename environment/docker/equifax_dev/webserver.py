from environment.docker.image import Image
from ansible.vulnerabilities import SetupStrutsVulnerability


class Webserver(Image):

    def __init__(self, name, ansible_runner, start_cmd=None):
        start_cmd = "/opt/tomcat/bin/startup.sh"
        super().__init__(name, ansible_runner, start_cmd)

    def ansible_provision(self):
        self.ansible_runner.run_playbook(
            SetupStrutsVulnerability("localhost", docker=True)
        )
