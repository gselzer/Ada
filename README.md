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

---

# Building Docker Container

```bash
docker build . -t ctnelson1997/ada
docker push ctnelson1997/ada
```

# Running Docker Container

```bash
sudo docker pull ctnelson1997/ada
sudo docker run --restart=always -d -e ENV_NAME=ada -p 5000:5000 ctnelson1997/ada

```
