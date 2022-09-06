---
title: Coati ACC Pipeline- README
---

# Coati_ACC_Pipeline
Predicts behavioural states from coati accelerometer data, among other things.

The following directory and file structure is needed for this program to run:

```
	PROJECTROOT/
	├── code/
	├── Data/
	│   ├── ethogram.tsv
	│   ├── acc/
	│   └── audits/
	├── Figures/
	└── tools/
```

The files in Data/acc must be generated using e-Obs DataDecoder, as specified below.
The files in Data/audits must be generated using BORIS, and config.py must reflect appropriate behaviours in the lists STATES, EVENTS, and METALABELS.

## Important notes:
1. Before using this software, use the DataDecoder provided by e-Obs to extract ACC data in columns with time data.
	To do this, first download the DataDecoder from [here](https://e-obs.de/service.htm).
	(The linux version is already available in the `tools/` directory here.
	Then, extract data from logger.bin files using the command

	```
	decoder -f <filename> -d <output-dir> -c 6 -a c
	```
2. This software uses the `locale` package in python, and sets it to `de_DE.utf8`.
	This change is necessary because the e-Obs DataDecoder saves time format with day-of-week in German (So, Mo, Di, Mi, Do, Fr, Sa).

	To do this on linux, you must first install the German locale 

	```sudo apt install language-pack-de```


