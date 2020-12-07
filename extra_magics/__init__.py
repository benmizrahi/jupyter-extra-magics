"""Extra Magics"""
__version__ = '1.0.0'

from .bq_estimation import BQEstimation  
from .bq_estimation import *
from .notifier import Notifier
from .notifier import *
from .super_run import SuperRun
from .super_run import *

def load_ipython_extension(ipython): 
    ipython.register_magics(BQEstimation)
    ipython.register_magics(Notifier)
    ipython.register_magics(SuperRun)