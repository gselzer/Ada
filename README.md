Ada is a work in progress.

It can be installed and run using the following steps:

# Installation

First, download [mamba](https://mamba.readthedocs.io/en/latest/installation.html#installation). If you would rather use [conda](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links), you can, but it will be slower.

From this directory:

```bash
mamba env create -f environment.yml
```

# Launching the Server

```
mamba activate ada
flask --app ada run
```