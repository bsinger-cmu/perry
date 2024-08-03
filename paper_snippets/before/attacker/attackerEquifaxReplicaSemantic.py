def get_low_level_action(self, ability_id):
    all_agent_links = await planning_svc.get_links(operation=operation, agent=agent)
    for link in all_agent_links:
        if link.ability.ability_id == ability_id:
            return link
    return None
async def main(self):
    if self.state == EquifaxAttackerState.InitialAccess:
        await self.initial_access()
    elif self.state == EquifaxAttackerState.CredExfiltrate:
        await self.cred_exfiltrate()
    elif self.state == EquifaxAttackerState.Finished:
        self.finished()
    return
async def initial_access(self):
    subnet_facts = await self.knowledge_svc_handle.get_facts(
        criteria=dict(
            trait="network.subnet.ip",
            source=self.operation.id,
        )
    )
    subnets = [fact.value for fact in subnet_facts]
    for subnet in subnets:
        await self.knowledge_svc_handle.add_fact(
            source=self.operation.id,
            fact="action.scan.ip",
            value=subnet,
        )
        scan_link = scan_link = get_low_level_action(self, HOST_ENUMERATION_ABILITY_ID)
        link_id = await operation.apply(scan_link)
        await operation.wait_for_links_completion([link_id])
        results = await self.knowledge_svc_handle.get_facts(
            criteria=dict(
                trait="host.ip",
                source=self.operation.id,
            )
        )
        host_ips = [fact.value for fact in results]
        for host_ip in host_ips:
            await self.knowledge_svc_handle.add_fact(
                source=self.operation.id,
                fact="action.scan.port",
                value=host_ip,
            )
            scan_link = get_low_level_action(self, PORT_SCAN_ABILITY_ID)
            link_id = await operation.apply(scan_link)
            await operation.wait_for_links_completion([link_id])
            host_facts = await self.knowledge_svc_handle.get_facts(
                criteria=dict(
                    trait="host.ip",
                    source=self.operation.id,
                )
            )
            open_host_ports = {}
            for host_ip_fact in host_facts:
                host_relationships = await self.knowledge_svc_handle.get_relationships(
                    criteria=dict(
                        source=host_ip_fact,
                        edge="open_port",
                    )
                )
                open_ports = [rel.target.value for rel in host_relationships]
                open_host_ports[host_ip_fact.value] = open_ports
    random.shuffle(open_host_ports)
    pre_agents = await self.knowledge_svc_handle.get_agents()
    for host_ip, open_ports in open_host_ports.items():
        for port in open_ports:
            if port == 80:
                await self.knowledge_svc_handle.add_fact(
                    source=self.operation.id,
                    fact="action.exploit.ip",
                    value=host_ip,
                )
                await self.knowledge_svc_handle.add_fact(
                    source=self.operation.id,
                    fact="action.exploit.port",
                    value=host_ip,
                )
                exploit_link = get_low_level_action(
                    self, APACHE_STRUTS_EXPLOIT_ABILITY_ID
                )
                link_id = await operation.apply(exploit_link)
                await operation.wait_for_links_completion([link_id])
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
                if infected_host:
                    break
    if not infected_host:
        raise Exception("Failed to infect any hosts")
    self.state = EquifaxAttackerState.CredExfiltrate
async def cred_exfiltrate(self):
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
                    if open_ports[infectedHostAgent.ip] == 80:
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
                        agents = await self.knowledge_svc_handle.get_agents()
                        for agent in agents:
                            exfiltrated_data = False
                            if open_ports[agent.ip] == 80:
                                has_ssh_creds = False
                                await self.knowledge_svc_handle.remove_facts(
                                    criteria=dict(
                                        trait="ssh.config",
                                        source=self.operation.id,
                                    )
                                )
                                ssh_config_link = get_low_level_action(self, SSH_CONFIG_ABILITY_ID)
                                link_id = await operation.apply(ssh_config_link)
                                await operation.wait_for_links_completion([link_id])
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
