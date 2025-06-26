## K-SPICE setup Tutorial 

### 1. Step One – Install Python 

To get started, you’ll need to install **Python version 3.12.10**.

👉 https://www.python.org/downloads/release/python-31210/


### 2. Step Two – Install Required Python Packages

Before using the K-SPICE API, you’ll need some extra Python tools (called "packages") that help with data handling, math, and plotting.

#### First, what is `pip`?

`pip` is a tool that lets you download and install other useful Python tools (called packages). It usually comes with Python, but if it’s missing, you can install it by running:

```bash
python -m ensurepip --upgrade

```

#### Then, install the packages:

Open your terminal or command prompt and run this one command to install everything at once:

```bash
python -m pip install matplotlib numpy pandas
```
