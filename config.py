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
    delimiter = input(f"""{os.path.basename(__file__)}: could not determine delimiter from {os.path.basename(eth_tgt)}.
                        It's usually ',' or '\\t' or something like that.
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
    'sniff',
    'chew stand',
    'chew headup'
]

EVENTS = [
    'drink',
    'self groom',
    'groom',
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
    assert (label in STATES) or (label in EVENTS) or (label in METALABELS), f"{label} not in STATES, EVENTS, or METALABELS"

for state in STATES:
    assert state in ETHOGRAM, f"{state} not in ETHOGRAM"

for event in EVENTS:
    assert event in ETHOGRAM, f"{event} not in ETHOGRAM"

for metalabel in METALABELS:
    assert metalabel in ETHOGRAM, f"{metalabel} not in ETHOGRAM"

### Feature extraction and audit reading
EPOCH = 2 #seconds
EPOCH_OVERHANG_TOLERANCE = 0.2
EPOCH_NAN_TOLERANCE = 0.2

IGNORE_EVENTS_IN_AUDITS = True

MULTIPLE_STARTS_ALLOWED = True
MULTIPLE_STARTS_WARNING = True

# TODO: add ML related terms
