# K-SPICE Setup Tutorial

This guide will help you set up everything you need to start working with the K-SPICE API.

---

## Table of Contents

1. [Step One – Install Python](#1. Step One – Install Python)
2. [Step Two – Install Required Python Packages](#2. Step Two – Install Required Python Packages)


### 1. Step One – Install Python

To get started, you’ll need to install **Python version 3.12.10**.

👉 https://www.python.org/downloads/release/python-31210/


Make sure to choose the correct installer as shown below:

![alt](images/python_download.png)



---

### 2. Step Two – Install Required Python Packages

Before using the K-SPICE API, you’ll need some extra Python tools (called "packages") that help with data handling, math, and plotting. We will start with downloading PIP. 

#### First, what is `pip`?

`pip` is a tool that lets you download and install other useful Python tools (called packages). It usually comes with Python, but if it’s missing, you can install it by running:

```bash
python -m ensurepip --upgrade

```

#### Then, install the packages:

```bash
python -m pip install matplotlib numpy pandas
```

This will install:

- `matplotlib` – for creating plots and graphs
- `numpy` – for working with numbers and arrays
- `pandas` – for handling data tables and CSV files

You can always come back to this step and install more packages later using the same format:

```shell
python -m pip install <library-name>
