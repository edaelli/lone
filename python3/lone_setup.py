#!/usr/bin/env python3
import os
import sys

# Add the current lone path to the beginning of the path
#  so we can run it from anywhere
lone_dir = os.path.abspath(os.path.join(__file__, '../'))
sys.path.insert(0, lone_dir)

# Import and run
from scripts import lone_setup  # NOQA
sys.exit(lone_setup.main())
