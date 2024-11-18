from .environment import Environment
from .specifications.equifax_large import EquifaxLarge
from .specifications.equifax_medium import EquifaxMedium
from .specifications.equifax_small import EquifaxSmall
from .specifications.ics import ICSEnvironment
from .specifications.ring import RingEnvironment

from .kali_environments.EquifaxKali import EquifaxKali

from .GoalKeeper import GoalKeeper
from .Result import ExperimentResult, FlagInformation, FlagType, DataExfiltrated

from .specifications.star import Star
from .specifications.dumbbell import Dumbbell
from .specifications.enterprise import Enterprise
