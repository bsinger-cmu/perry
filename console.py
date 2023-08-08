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
        self.completed = 0
        self.time_last_updated = 0.0

    def render(self, task):
        # I do not know why this doesn't work when the time between updates is really wrong
        # (specifically in the case of using it for running experiment trials)
        # and at this point I give up. If anyone wants to attempt to fix it, good luck and godspeed.
        if task.elapsed is None:
            return Text('-:--:--', style='white')
        
        if task.completed > self.completed:
            self.time_last_updated = task.elapsed
            self.completed = task.completed

        elapsed = task.finished_time - self.time_last_updated if task.finished else task.elapsed - self.time_last_updated
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
    speed_estimate_period=1000,
    expand=True,
    redirect_stderr=True,
    redirect_stdout=True,
    # transient=True,
)