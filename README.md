# K-SPICE API - Setup Tutorial

CURRENTLY WORK IN PROGRESS...

This guide will help you set up everything you need to start working with the K-SPICE API.



## Table of Contents

1. [Python Installation](#step-one---install-python)
2. [Package Installation In Python](#step-two-package-installation)
3. [Setting Up Visual Studio Code editor](#step-three--set-up-visual-studio-code-editor)
4. [Folder Structure](#step-four--folder-structure)
5. [Configuration Of Path variables](#step-five--configure-path-variables)
6. [Test Run](#step-six--do-a-test-run)

---

## Step One - Install Python 

To get started, you’ll need to install **Python version 3.12.10**.

👉 https://www.python.org/downloads/release/python-31210/

Make sure to select the correct installer for your system, as shown below:

![alt](images/python_download.png)

Double-click the downloaded file. You should see a window like this:

![alt](images/python_installer.jpg)

Chcek the "Add python.exe to PATH" and then click on "Customize installation" and check the boxes for:

![alt](images/python2.png)

Click on "Next" and check the following options:
- **pip** (Python package manager)
- **Documentation**

![alt](images/python3.png)

Click "Install" to complete the installation. 

---

## Step Two Package Installation 

Before using the K-SPICE API, you’ll need some extra Python tools (called "packages") that help with data handling, math, and plotting. 
### First, open the Command Prompt window by either:

- Typing `cmd` in the Windows search bar and pressing **Enter**, or  
- Pressing **Windows key + R**, typing `cmd`, then pressing **Enter**

If done correctly a window similar to this shoudl pop up on your screen: 

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


This should be pretty straightforward — just follow the necessary steps in the **VS Code installer**.

Once the installation is complete and you open the application:

1. Go to the **Extensions** tab  
   (you can also press `Ctrl+Shift+X` on your keyboard)

2. In the search bar, type **"Python"**

3. Look for the extension published by **Microsoft** and click **Install**

The screenshot below shows where to find the Extensions tab and which Python extension to install:

https://youtu.be/cu_ykIfBprI?feature=shared

![cmd](images/extensions.jpg)

## Step Four – Folder Structure 

If you have used K-Spice before without the API you probably have this step completed, however for first time users make sure that you store your project files in a proper way that K-spice easliy can read them.

![cmd](images/k_spice_start.png)

## Step Five – Configure Path Variables

Open up the search bar in windows and type in "edit enviroment variables for your account" and open it. A window like this shoudl pop up: 


![cmd](images/enviroment_variables.png)
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

### Testing in debug mode 
