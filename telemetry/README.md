`ansible-playbook install.yml --extra-vars "username=yinuo my_package_url=https://github.com/sysflow-telemetry/sf-collector/releases/download/0.5.0/sfcollector-0.5.0-x86_64.deb my_package_name=sysflow_package my_package_url_2=https://github.com/sysflow-telemetry/sf-processor/releases/download/0.5.0/sfprocessor-0.5.0-x86_64.deb my_package_name_2=sysflow_package_2 my_package_url_3=https://github.com/sysflow-telemetry/sf-collector/releases/download/0.5.0/libsysflow-0.5.0-x86_64.deb my_package_name_3=libsysflow" -K
`

- [ ] Collect data from remote host
- [ ] Write a policy rule to detect attack
- [ ] Integrate Elastic