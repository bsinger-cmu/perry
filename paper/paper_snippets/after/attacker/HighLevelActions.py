class HighLevelAction:
    async def execute(self):
        pass


class InfectHost(HighLevelAction):
    pass


class ScanNetwork(HighLevelAction):
    pass


class DiscoverHostInformation(HighLevelAction):
    pass


class ExfiltrateData(HighLevelAction):
    pass
