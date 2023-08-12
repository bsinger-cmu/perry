from datetime import timedelta
from typing import Optional
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TaskProgressColumn,
    MofNCompleteColumn,
    TransferSpeedColumn,
    SpinnerColumn,
    ProgressColumn,
    Text
)
from rich.table import Column
class TaskTimeElapsedColumn(ProgressColumn):
    """Renders elapsed time for a portion of a task; time elapsed for the mth job to complete out of n total jobs."""
    def __init__(self, table_column: Column | None = None) -> None:
        super().__init__(table_column)
        self.completed = {}
        self.time_last_updated = {}

    def render(self, task):
        if task.id not in self.completed:
            self.completed[task.id] = 0
            self.time_last_updated[task.id] = 0
        
        
        if task.elapsed is None:
            return Text('-:--:--', style='white')
        
        if task.completed > self.completed[task.id]:
            self.time_last_updated[task.id] = task.elapsed
            self.completed[task.id] = task.completed

        if task.completed < self.completed[task.id] and task.completed == 0:
            self.time_last_updated[task.id] = 0
            self.completed[task.id] = 0

        elapsed = task.finished_time - self.time_last_updated[task.id] if task.finished else task.elapsed - self.time_last_updated[task.id]
        delta = timedelta(seconds=max(0, int(elapsed)))
        return Text(str(delta), style="white")


console = Console()


progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(bar_width=None),
    TaskProgressColumn(),
    MofNCompleteColumn(),
    TaskTimeElapsedColumn(),
    "•",
    TimeRemainingColumn(), 
    TimeElapsedColumn(),
    console=console,
    auto_refresh=True,
    refresh_per_second=5,
    speed_estimate_period=3600,
    expand=True,
    redirect_stderr=True,
    redirect_stdout=True,
    # transient=True,
)