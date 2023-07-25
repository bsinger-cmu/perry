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
)
console = Console()
progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    MofNCompleteColumn(),
    TimeRemainingColumn(), 
    TimeElapsedColumn(),
    console=console,
    refresh_per_second=10,
    redirect_stderr=True,
    redirect_stdout=True,
    expand=True,
    # transient=True,
)