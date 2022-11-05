try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from .feature_histogram import *  # NoQA
from .histogram import *  # NoQA
from .scatter import *  # NoQA
from .slice import *  # NoQA
