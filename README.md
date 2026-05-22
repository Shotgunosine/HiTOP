
# HiTOP_validation_submission

This is a repo for code accompanying the manuscript "Test-Retest reliability and measurement invariance of a subset of the HiTOP internalizing scales with a two-week time window"

# Authors

[Marie Zelenina](https://github.com/mariezelenina)

Francisco Pereira

[Dylan M. Nielson](https://github.com/Shotgunosine)

# Preregistration

- https://osf.io/xpa7v/

# Abstract

This is the repostory for the code used for the manuscript "Test-Retest reliability and measurement invariance of a subset of the HiTOP internalizing scales with a two-week time window". 

The Hierarchical Taxonomy of Psychopathology (HiTOP) is a novel way of measuring psychopathology, which addresses problems of existing measures.
The validated HiTOP scales have a 1-year assessment window. This poses a challenge for relating them to individual performance on cognitive tasks collected in a single day, 
as is common in research. We created a version of the scales more relevant for computational psychiatry by assessing symptoms over 2 weeks, using a subset of scales that were most relevant for depression and anxiety.
We confirmed that the scales measure the same underlying constructs as the original, 1-year scales, with confirmatory factor analysis (CFA); analyzed their test-retest reliability with intracalss correlations (ICC), 
and tested their convergent and divergent validity against existing robust scales.

# How to run the code

All preprocessing and analyses were conducted in Python, using Jupyter Notebooks.

All code should be run in this order, cell by cell, changing paths as appropriate:

+ **NB_1_preprocess_and_descriptive.ipynb** preprocesses raw data and collects descriptive statistics.
+ **NB_2_cfa.ipynb** runs confirmatory factor analysis.
+ **NB_3_ICC.ipynb** runs test-retest reliability analysis.
+ **NB_4_convdiv.ipynb** tests convergent and divergent hypotheses.
+ ***NB_icc_plots.ipynb*** is used to produce Fig. 3 (ICC results).

If you come across an issue, please submit it in this repository or reach out to [Marie Zelenina](https://github.com/mariezelenina) or [Dylan Nielson](https://github.com/Shotgunosine) with questions.

# Where/how to get the data

TODO after data sharing.

## How to install dependencies

We use the following python libraries: 

*jupyter notebook, pandas, numpy, matplotlib, sklearn (scikit-learn), scipy, itertools, openpyxl, contextlib, random, math, seaborn, datetime, csv, pingouin, statsmodels, pathlib, rpy2*

and the following R packages (for CFA analysis):

*lavaan, semTools, stringr, reticulate (+ base and utils)*

The CFA code uses a mix of python and R libraries, so it might get tricky. For integration between pythion and R, we used the version of rpy2=3.5.1, r-base=4.2.3. 

### Pixi instructions (recommended):

Install (pixi)[https://pixi.prefix.dev/latest/#quick-demo] if you don't have it.
Use pixi to run the `install_r_libraries.py` script. For some reason the compatible versions of some packages we need aren't on conda-forge, so we have to  `install.packages` instead.
`pixi run ./install_r_libraries.py`

After that, you can run a jupyter lab session and execute our notebooks.
`pixi run jupyter lab`

### Conda instructions:
You can create a conda environment with:

`conda env create -p ./env -f environment_hitop.yml`

Then activate the conda environment. BE SURE YOU HAVE ACTIVATED YOUR ENV. The following command is going to install some r libraries, if you haven't activated your conda env, they could get installed who knows where. The run this command:
`python ./install_r_libraries.py`



