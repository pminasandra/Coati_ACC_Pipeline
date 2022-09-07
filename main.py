# Pranav Minasandra
# pminasandra.github.io
# September 06, 2022

import glob
import os
import os.path

import accreading
import auditreading
import config

# First read all available audit data
print(auditreading.read_all_audits())

# Then extract all features for all feature-space
# Train the classifiers
# Perform analyses
