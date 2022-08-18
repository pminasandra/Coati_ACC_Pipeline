# Pranav Minasandra
# pminasandra@ab.mpg.de
# August 18, 2022

import os.path

import pandas as pd

### Setting up directories
PROJECTROOT = "/media/pranav/Data1/Personal/Projects/Coati_ACC_Pipeline_2022/"
FIGURES_DIR = os.path.join(PROJECTROOT, "Figures/")
DATA_DIR = os.path.join(PROJECTROOT, "Data/")

#SERVER_PROJECTROOT = "/media/pranav/MPI_Dirs/EAS_shared/coati/working/Coati_ACC_Pipeline/"
SERVER_PROJECTROOT = "/media/pranav/MPI_Dirs/EAS_shared/ccas/working/Coati_ACC_Pipeline"
ACCELEROMETER_DATA = os.path.join(SERVER_PROJECTROOT, "working/Coati_ACC_Pipeline/Data/Accelerometer/")
AUDIT_DATA = os.path.join(SERVER_PROJECTROOT, "working/Coati_ACC_Pipeline/Data/Audits/")

### Setup, generate lists of behaviours

_unknown_behaviour_labels = ["NA", "UNKNOWN"]

eth_tgt = os.path.join(DATA_DIR, "ethogram.tsv") #FIXME: Ideally, this should be on the server so that all changes can immediately be tracked.
if eth_tgt[-4:] == ".tsv":
    delimiter = "\t"
elif eth_tgt[-4:] == ".csv":
    delimiter = ","
else:
    delimiter = input(f"""config.py: could not determine delimiter from {os.path.basename(eth_tgt)}.\n
                        It's usually ',' or '\\t' or something like that.\n
                        Enter it here (without quotation marks):""")

ETHOGRAM = list(pd.read_csv(eth_tgt, sep=delimiter)['Behavior code'])

STATES = [
    'forage',
    'walk',
    'tree climb up',
    'tree climb down',
    'stand still',
    'sit still',
    'chewdown',
    'lope',
    'run',
    'standup',
    'lie',
    'chew stand',
    'chew headup'
]

EVENTS = [
    'drink',
    'self groom',
    'groom',
    'sniff',
    'agg to',
    'spin',
    'agg from',
    'lick',
    'headup',
    'call',
    'bounce',
    'headbop',
    'backleg scratch',
    'scratch stomach',
    'head shake'
]

METALABELS = [
    'time'
]


### Validating state/event/meta classifications
for label in ETHOGRAM:
    assert (label in STATES) or (label in EVENTS) or (label in METALABELS)

for state in STATES:
    assert state in ETHOGRAM

for event in EVENTS:
    assert event in ETHOGRAM

for metalabel in METALABELS:
    assert metalabel in ETHOGRAM

