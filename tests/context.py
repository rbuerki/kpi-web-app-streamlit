# Helps with imports of source code files by manipulating class path, see here for more:
# https://towardsdatascience.com/ultimate-setup-for-your-next-python-project-179bda8a7c2c

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import kpi_sheet  # noqa: E402, F401
