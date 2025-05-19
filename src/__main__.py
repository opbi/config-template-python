"""Package Structure Convention.

top level scaffold to thread args and process.
"""

from .args import parse_args
from .process import process
from .shared.args import parse_env_vars
from .shared.logger import config_logger

parse_env_vars()
args = parse_args()
config_logger()
process(args)
