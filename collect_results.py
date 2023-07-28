
import argparse
from datetime import datetime
import json
import os
from abc import ABC, abstractmethod
import csv
from rich import print as rprint

from rich.console import Console
from rich.table import Table
from rich.terminal_theme import MONOKAI

console = Console(record=True)


class Filters:
    def __init__(self) -> None:
        self.filters = []
        self.condition_classes = {
            "eq": self.Equals,
            "neq": self.NotEquals,
            "dne": self.DoesNotExist,
        }
    
    # Add a filter to the list of filters
    def add_filter(self, filter_str):
        key, filter_type, value = filter_str.split(":")
        if filter_type not in self.condition_classes:
            print(f"Filter type '{filter_type}' not supported.")
            raise Exception("Filter type not supported.")
        
        condition_class = self.condition_classes[filter_type]
        self.filters.append(condition_class(key, value))
    
    def add_all_filters(self, filters):
        for filter_str in filters:
            self.add_filter(filter_str)

    # Check if all filters are true
    # TODO: Add support for OR and AND
    def check_all(self, data):
        return all([filter.check(data) for filter in self.filters])

    class Condition(ABC):
        def __init__(self, key, value) -> None:
            self.key = key
            self.value = value
        @abstractmethod
        def check(self, data):      
            pass

    class Equals(Condition):
        def check(self, data):
            return self.key in data.keys() and data[self.key] == self.value

    class NotEquals(Condition):
        def check(self, data):
            return self.key in data.keys() and data[self.key] != self.value
    
    class DoesNotExist(Condition):
        def check(self, data):
            return self.key not in data.keys()


class Collector():
    def __init__(self, start_datetime, end_datetime, search_dir="metrics", output_dir="results"):
        self.search_dir = search_dir
        self.output_dir = output_dir
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        
        self.files = []
        self.filtered_file_names = []
        self.filtered_files = []

    def collect_files(self):
        for file in os.listdir(self.search_dir):
            if file.endswith(".json") and file.startswith("metrics-"):
                date_str = file.split("metrics-")[1].split(".json")[0]
                date = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
                if self.start_datetime <= date and date <= self.end_datetime:
                    self.files.append(file)

    def filter_files(self, conditions):
        for file in self.files:
            with open(f"{self.search_dir}/{file}", 'r') as f:
                data = json.load(f)
                if filters.check_all(data):
                    self.filtered_files.append(data)
                    self.filtered_file_names.append(file.split(".json")[0])
        self.filtered_file_names.sort()
        print(f"Filtered {len(self.files)} files down to {len(self.filtered_files)} files.")
        if len(self.filtered_file_names) > 0:
            print(f"From {self.filtered_file_names[0]} to {self.filtered_file_names[-1]}")
        # for file in self.filtered_file_names:
        #     print(f"\t{file}")

    def _export_csv(self, filename):
        if len(self.filtered_files) == 0:
            print("No files to export.")
            return
        
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.filtered_files[0].keys())
            writer.writeheader()
            for data in self.filtered_files:
                writer.writerow(data)

    def export_file(self, filename):
        filetype = filename.split(".")[-1]

        if filetype == "csv":
            self._export_csv(f"{self.output_dir}/{filename}")
        else:
            raise Exception(f"File type {filetype} not supported.")
    
    def print_experiment_metrics(self):
        total_experiments   = len(self.filtered_files)
        if total_experiments == 0:
            print("No experiments to print metrics for.")
            return
        
        avg_experiment_time = round(sum([data['experiment_time'] for data in self.filtered_files]) / len(self.filtered_files), 2)
        avg_execution_time  = round(sum([data['execution_time'] for data in self.filtered_files]) / len(self.filtered_files), 2)
        avg_setup_time      = round(sum([data['setup_time'] for data in self.filtered_files]) / len(self.filtered_files), 2)
        max_flags_captured  = max([len(data['flags_captured']) for data in self.filtered_files])
        min_flags_captured  = min([len(data['flags_captured']) for data in self.filtered_files])
        max_root_flags_captured = max([len(data['root_flags_captured']) for data in self.filtered_files])
        min_root_flags_captured = min([len(data['root_flags_captured']) for data in self.filtered_files])

        flags_captured_count = {}
        root_flags_captured_count = {}
        total_time = sum([data['experiment_time'] for data in self.filtered_files])

        total_restores_per_host = { }
        total_host_restores = 0

        for data in self.filtered_files:
            num_flags_captured = len(set(data['flags_captured']))
            num_root_flags_captured = len(set(data['root_flags_captured']))
            
            if num_flags_captured not in flags_captured_count:
                flags_captured_count[num_flags_captured] = 1
            else:
                flags_captured_count[num_flags_captured] += 1

            if num_root_flags_captured not in root_flags_captured_count:
                root_flags_captured_count[num_root_flags_captured] = 1
            else:
                root_flags_captured_count[num_root_flags_captured] += 1
            
            if 'count_host_restores' in data:
                for host, count in data['count_host_restores'].items():
                    if host not in total_restores_per_host:
                        total_restores_per_host[host] = count
                    else:
                        total_restores_per_host[host] += count
            
        
        flags_captured_count = dict(sorted(flags_captured_count.items()))
        root_flags_captured_count = dict(sorted(root_flags_captured_count.items()))
        
        if len(total_restores_per_host.items()) > 0:
            total_host_restores = sum([data['total_host_restores'] for data in self.filtered_files])
            average_host_restores = round(total_host_restores / total_experiments, 2)
            total_restores_per_host = dict(sorted(total_restores_per_host.items()))
            average_restores_per_host = { host: round(count / total_experiments, 2) for host, count in total_restores_per_host.items() }
            average_restores_per_host = dict(sorted(average_restores_per_host.items()))

        print("")
        print("*"*80)
        print("* Experiment Metrics")
        print("*"*80)
        print("")
        print(f"Total Experiments:         {total_experiments}")
        print(f"Total Time:                {round(total_time/3600, 2)} hours")
        print("")
        print(f"Average Setup Time:        {avg_setup_time} seconds ({round(avg_setup_time/60, 2)} minutes)")
        print(f"Average Execution Time:    {avg_execution_time} seconds ({round(avg_execution_time/60, 2)} minutes)")
        print(f"Average Experiment Time:   {avg_experiment_time} seconds ({round(avg_experiment_time/60, 2)} minutes)")

        # table = Table(show_header=False, header_style="bold hot_pink")
        # table.add_column("Metric")
        # table.add_column("Value")
        # table.add_row("Average Setup Time", f"{avg_setup_time} seconds ({round(avg_setup_time/60, 2)} minutes)")
        # table.add_row("Average Execution Time", f"{avg_execution_time} seconds ({round(avg_execution_time/60, 2)} minutes)")
        # table.add_row("Average Experiment Time", f"{avg_experiment_time} seconds ({round(avg_experiment_time/60, 2)} minutes)")
        # console.print(table)

        print("")
        print(f"Min Flags Captured:        {min_flags_captured}")
        print(f"Max Flags Captured:        {max_flags_captured}")
        print("")
        print(f"Min Root Flags Captured:   {min_root_flags_captured}")
        print(f"Max Root Flags Captured:   {max_root_flags_captured}")
        print("")

        # table = Table(show_header=True, header_style="bold hot_pink")
        # table.add_column("Flags Captured")
        # table.add_column("Count")
        # table.add_column("Percentage")
        # for num_flags_captured, count in flags_captured_count.items():
        #     table.add_row(f"{num_flags_captured}", f"{count}", f"{round(count/total_experiments*100,2)}%")
        # console.print(table)

        # table = Table(show_header=True, header_style="bold hot_pink")
        # table.add_column("Root Flags Captured")
        # table.add_column("Count")
        # table.add_column("Percentage")
        # for num_flags_captured, count in root_flags_captured_count.items():
        #     table.add_row(f"{num_flags_captured}", f"{count}", f"{round(count/total_experiments*100,2)}%")
        # console.print(table)

        print("Flags Captured Count:")
        for num_flags_captured, count in flags_captured_count.items():
            print(f"\t{num_flags_captured} Flags: {count:<5} times ({round(count/total_experiments*100,2)}%)")
        print("")
        print("Root Flags Captured Count:")
        for num_flags_captured, count in root_flags_captured_count.items():
            print(f"\t{num_flags_captured} Flags: {count:<5} times ({round(count/total_experiments*100,2)}%)")

        if total_host_restores > 0:
            print("")
            print(f"Total Restores:   {total_host_restores}")
            print(f"Average Restores:   {average_host_restores}")
            print("")
            print("Total Restores Per Host:")
            for host, count in total_restores_per_host.items():
                print(f"\t{host}: {count} restores")
            print("")
            print("Average Restores Per Host:")
            for host, count in average_restores_per_host.items():
                print(f"\t{host}: {count} restores")
        
        print("")
        print("*"*80)
        print("")
        # console.save_svg(f"{self.output_dir}/metrics.svg")
        

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-s', '--start-datetime', help='Start of time range to collect files', required=False, default=datetime.min)
    argparser.add_argument('-e', '--end-datetime', help='End of time range to collect files', required=False, default=datetime.max)
    
    argparser.add_argument('-o', '--output', help='Output file to save results to', required=False, default="results.csv")
    argparser.add_argument('-f', '--filters', help='Filters to apply to collected files', required=False, nargs='*')
    
    argparser.add_argument('-d', '--subdir', help='Search a specific subdirectory', required=False)
    argparser.add_argument('-r', '--rootdir', help='Search a specific root directory', required=False, default="metrics")

    argparser.add_argument('-v', '--verbose', help='Verbose output', required=False, action='store_true', default=False)

    args = argparser.parse_args()

    if args.start_datetime == datetime.min:
        start_datetime = datetime.min
    else:
        start_datetime = datetime.strptime(args.start_datetime, "%Y-%m-%d_%H-%M-%S")
    
    if args.end_datetime == datetime.max:
        end_datetime = datetime.max
    else:
        end_datetime = datetime.strptime(args.end_datetime, "%Y-%m-%d_%H-%M-%S")
    
    filters = Filters()
    if args.filters:
        filters.add_all_filters(args.filters)


    search_dir = args.rootdir
    output_dir = "results"

    if args.subdir:
        search_dir = os.path.join(args.rootdir, args.subdir)
        output_dir = os.path.join(output_dir, args.subdir)

    # Check tthat the directory exists
    if not os.path.isdir(search_dir):
        raise Exception(f"Directory {search_dir} does not exist.")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    print(f"Will search directory '{search_dir}' for files between {start_datetime} and {end_datetime}...")
    print(f"Will save results to '{output_dir}/{args.output}'...")

    result_collector = Collector(start_datetime, end_datetime, search_dir, output_dir)
    result_collector.collect_files()
    result_collector.filter_files(filters)
    result_collector.export_file(args.output)
    if args.verbose:
        result_collector.print_experiment_metrics()
