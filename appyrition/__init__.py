"""
This module provides a Python API Client for the Ghost content platform:
https://ghost.org/

It provides a set of functions to interact with the Ghost Admin API endpoints
which allow publishing and updating posts.

The goal is to allow developers to create and track posts using local markdown
and git and deploy to Ghost without copying and pasting into the Ghost editor.

Please refer to the documentation provided in the README.md, which can be found
at the Assimilate Dev Github page: https://github.com/assimilate-dev/appyrition
"""

from .appyrition import Ghost
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
