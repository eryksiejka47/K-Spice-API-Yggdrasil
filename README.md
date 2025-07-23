# K-SPICE API - Setup Tutorial

This guide will help you set up everything you need to start working with the **K-SPICE API**.  
> **Note:** This tutorial assumes that **K-SPICE** is already installed on your system.

## Table of Contents

1. [Python Installation](#step-one---install-python)
2. [Package Installation In Python](#step-two---package-installation)
3. [Setting Up Visual Studio Code editor](#step-three--set-up-visual-studio-code-editor)
4. [Folder Structure](#step-four--folder-structure)
5. [Configuration Of Path variables](#step-five--configure-path-variables)
6. [Test Run](#step-six--do-a-test-run)
7. [How to use?](#how-to-use)


---

## Step One - Install Python 

Before downloading Python, it is important to verify that you have the necessary package on your device and determine which Python version is compatible with it.

### Verifying the K-Spice API Package

First, we need to verify that the **K-Spice API package** is located in the `bin64` folder.

In the screenshot below, we can see the following file:

`
kspice.cp312-win_amd64
`

This filename provides useful information:

- **`cp312`**: Indicates compatibility with **Python 3.12**.
- **`win_amd64`**: Specifies that the package is intended for **64-bit Windows systems**.

![cmd](images/bin64.PNG)

Based on the information we’ve gathered above, we need to install Python 3.12. After speaking with people at Kongsberg, they recommended installing version 3.12.10. I’m not entirely sure why, but I assume that any 3.12 version should work.

We therefore start by installing **Python version 3.12.10**:

👉 https://www.python.org/downloads/release/python-31210/

Make sure to select the correct installer for your system, as shown below:

![alt](images/python_download.png)

Double-click the downloaded file. You should see a window like this:

![alt](images/python_installer.jpg)

Chcek the `Add python.exe to PATH` and then click on `Customize installation` and check the boxes for:

![alt](images/python2.png)

Click on "Next" and check the following options:
- **pip** (Python package manager)
- **Documentation**

![alt](images/python3.png)

Click `Install` to complete the installation. 

---

## Step Two - Package Installation 

Before using the K-SPICE API, you’ll need some extra Python tools (called "packages") that help with data handling, math, and plotting. 
### First, open the Command Prompt window by either:

- Typing `cmd` in the Windows search bar and pressing **Enter**, or  
- Pressing **Windows key + R**, typing `cmd`, then pressing **Enter**

If done correctly a window similar to this should pop up on your screen: 

![cmd](images/cmd_picture.PNG)

#### Installing `pip`

`pip` is a tool that lets you download and install other useful Python packages. It usually comes with Python, but if it’s missing, you can install it by running:

```bash
python -m ensurepip --upgrade

```

#### Then, install the packages:

```bash
python -m pip install matplotlib numpy pandas datetime
```

This will install:

- `matplotlib` – for creating plots and graphs
- `numpy` – for working with numbers and arrays
- `pandas` – for handling data tables and CSV files
- `datetime` – for handling timelines

You can always come back to this step and install more packages later using the same format:

```shell
python -m pip install <library-name>
```

## Step Three – Set up Visual Studio Code editor


To run your Python scripts, you need to install an environment that supports Python execution.

I recommend using **Visual Studio Code (VS Code)**, and I’ll quickly guide you through how to set it up. However, feel free to use any environment you prefer — if you already have a favorite, go for it!

#### Why VS Code?
- Lightweight and fast
- Great Python support with extensions
- Built-in terminal and debugger
- Works on Windows, macOS, and Linux

You can **Download and install VS Code** by following the link down below: 

👉https://code.visualstudio.com/download


This should be pretty straightforward — just follow the necessary steps in the *VS Code installer*, however if you struggle check out the video down below: 

👉https://youtu.be/cu_ykIfBprI?feature=shared

Once the installation is complete and you open the application:

1. Go to the **Extensions** tab (you can also press `Ctrl+Shift+X` on your keyboard)

2. In the search bar, type **"Python"**

3. Look for the extension published by **Microsoft** and click **Install**

The screenshot below shows where to find the Extensions tab and which Python extension to install:



![cmd](images/extensions.jpg)

## Step Four – Folder Structure 

If you have used K-Spice before without the API you probably have this step completed, however for first time users make sure that you store your project files in a proper way that K-spice easliy can read them.

Create a folder on your **C: drive** with any name you like.  
In the screenshot below, you’ll see I named mine **K-Space-Projects** — this is just to illustrate that you can choose whatever name suits you.

Keep all your **K-Spice projects** organized inside this folder.


![cmd](images/path_projects.png)

Just remember to specify in **K-Spice Sim Explorer** which folder you’re using to store your projects:

![cmd](images/k_spice_start.png)


## Step Five – Configure Path Variables

Open up the search bar in windows and type in "edit enviroment variables for your account" and open it. A window like this should pop up: 

![cmd](images/enviroment_variables.png)

We need to add a new user variable, therefore press "New..." and name the variable "PYTHONPATH". Next, copy and paste the line below in the "Variable value" field:

```shell
C:\Program Files (x86)\Kongsberg\K-Spice\bin64
```
It should look like this:

![cmd](images/PYTHONPATH.png)

## Step six – Do a test run.

Use the code below to. If it compiled Congratulations you can start with the K-Spice API

```python
# Importing necessary libraries
import pandas as pd
import numpy as np
from datetime import timedelta
import csv
import kspice

# Version Check
print("KSPICE version:", kspice.__version__)

# Path for project folder 
sim = kspice.Simulator(r"C:\K-Spice-Projects\DemoProject") 

# Activvating the timeline
tl = sim.timelines[0]
tl.activate()

# Load models, parameters, initial_conditions 
tl.load("KSpiceTutorial Model", "KSpiceTutorial Model", "Steady_state")

# Run timeline for 120 seconds 
sim_time = timedelta(seconds=120)
tl.run_for(sim_time)

# Deactivate the timeline
tl.deactivate()

# Close project 
sim.close_project()
```

If you get an error that the Kspice library is not found try including it this way: 

```python

import sys
sys.path.append(r"C:/Program Files (x86)/Kongsberg/K-Spice/bin64")
import kspice
```

## How to use? 
Using the K SPICE API allows us to automate testing workflows efficiently. You can program your own test sequences, run them at any time including overnight to save working hours, and export the results to CSV files. From there, Python offers a wide range of tools for data processing, plotting, and analysis. It provides a flexible and powerful environment for working with simulation data.

This chapter gives a brief introduction to how the API works and what resources are available to help you get started.

First of all, you can find the official K-Spice documentation [here](https://akerbp.sharepoint.com/:f:/s/E2EProductionOptimizationAutomatedwellcontrol/Eo5NKqmLq5tErv02UsjdYksB1yE4VbWZFjLQCPJPQQWRUg?e=yiTFJr).
Download the folder to your device to view the contents. Please note that this documentation is not publicly available.








