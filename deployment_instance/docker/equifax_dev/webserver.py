from deployment_instance.docker.image import Image
from ansible.vulnerabilities import SetupStrutsVulnerability


class Webserver(Image):

    def ansible_provision(self):
        self.ansible_runner.run_playbook(
            SetupStrutsVulnerability("localhost", docker=True)
        )
