"""rpy2/R session setup shared by the CFA notebooks.

Importing this module starts the embedded R session, so the BLAS threading
environment variables must be set before rpy2 loads R
(https://github.com/rpy2/rpy2/issues/882). The pixi environment sets them via
[activation.env]; they are also set here (without overriding existing values)
in case the interpreter was launched outside a pixi shell.
"""
import os
import random

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import rpy2.robjects as ro
import rpy2.rinterface_lib.callbacks
from rpy2.rinterface_lib.embedded import RRuntimeError
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr

rbase = importr('base')
utils = importr('utils')
lavaan = importr('lavaan')
semtools = importr('semTools')


def set_seeds(seed=12345):
    # seed both python and R; permuteMeasEq forks workers, hence L'Ecuyer-CMRG
    random.seed(seed)
    ro.r('RNGkind(kind = "L\'Ecuyer-CMRG")')
    ro.r(f'set.seed({seed})')


def silence_r():
    """Silence R console output and warnings.

    Be careful doing this, you might miss important warnings.
    """
    def _noop(x):
        pass

    rpy2.rinterface_lib.callbacks.consolewrite_print = _noop
    rpy2.rinterface_lib.callbacks.consolewrite_warnerror = _noop
