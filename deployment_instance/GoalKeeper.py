import time

class GoalKeeeper:

    def __init__(self, attacker):
        self.attacker = attacker

        return
    
    def setup(self, flags):
        # Save flags
        self.flags = flags

        # Start a timer
        self.start_time = time.time()
        return
    
    def check_flag(self, flag):
        for host, flag_value in self.flags.items():
            if flag_value == flag:
                return host
        
        return None

    def calculate_metrics(self):
        # TODO: Make this an object
        self.metrics = {}

        # Calculate time elapsed
        elapsed_time = time.time() - self.start_time
        self.metrics['time_elapsed'] = elapsed_time

        # Record flags captured
        flags_captured = []
        relationships = self.attacker.get_relationships()
        for relationship in relationships:
            if relationship['source']['value'] == 'flag.txt' and relationship['edge'] == 'has_contents':
                host_flag_captured = self.check_flag(relationship['target']['value'])
                if host_flag_captured is not None:
                    flags_captured.append(host_flag_captured)

        self.metrics['flags_captured'] = flags_captured
        return self.metrics
