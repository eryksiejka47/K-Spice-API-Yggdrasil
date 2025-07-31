# Importing necessary libraries
import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
import csv
import kspice

##################################################################################################################################################
############################################################ Functions ###########################################################################
##################################################################################################################################################

def run_and_sample(timeline, selected_app, variables, minutes, samples): 
    """ 
    Runs the simulation for a given number of minutes, samples data every second,
    and appends it to the samples list. Optionally logs a label for the session.

    Parameters:
    timeline: The active K-Spice timeline object.
    selected_app: The application name within the timeline.
    variables: List of variables to sample.
    minutes: Duration of the simulation in minutes.
    samples: List to store the sampled data.
    text: A label or description for the sampling session.

    """
    total_seconds = minutes * 60
    for i in range(total_seconds):
        timeline.run_for(timedelta(seconds=1))
        sample = timeline.get_values(selected_app, variables)
        sample.insert(0, timeline.model_time.total_seconds())
        samples.append(sample)


def adjust_parameter(timeline, selected_app, parameter_name, multiplier):
    """
    Adjusts a given parameter by a multiplier and sets the new value in the simulation.

    Parameters:
    timeline: The active K-Spice timeline object.
    selected_app: The application name within the timeline.
    parameter_name (str): The name of the parameter to adjust.
    multiplier (float): The factor by which to multiply the current value (e.g., 1.1 for +10%, 0.9 for -10%).
    """
    current_val = timeline.get_value(selected_app, parameter_name)
    print(f"Current value of {parameter_name}: {current_val}")
    
    new_val = current_val * multiplier
    timeline.set_value(selected_app, parameter_name, new_val)
    
    print(f"Updated {parameter_name} to {new_val} ({multiplier * 100:.1f}% of original)")


def change_valve_by_value(timeline, selected_app, parameter_name, change_value):
    """
    Adjusts a given parameter by adding or subtracting a specific value.

    Parameters:
    timeline: The active K-Spice timeline object.
    selected_app: The application name within the timeline.
    parameter_name (str): The name of the parameter to adjust.
    change_value (float): The value to add or subtract (e.g., +10 or -25).
    """
    current_val = timeline.get_value(selected_app, parameter_name)
    print(f"Current value of {parameter_name}: {current_val}")
    
    new_val = current_val + (change_value/100)
    timeline.set_value(selected_app, parameter_name, new_val)
    
    print(f"Updated {parameter_name} to {new_val} (change of {change_value:+.1f})")


def save_samples_to_csv(filename):
    """
    Saves the simulation samples to a CSV file with headers including variable names and units.

    Parameters:
    filename (str): The name of the CSV file to save the data to.
    """
    # Create a copy of the variables list to construct the header row
    header_row = variables.copy()
    
    # Insert the model time as the first column
    header_row.insert(0, ["ModelTime", "s"])
    
    # Flatten the header row to create readable column names
    header_row_flat = [f"{var[0]} [{var[1]}]" if isinstance(var, list) else var for var in header_row]
    
    # Write the header and sample data to the CSV file
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header_row_flat)  # Write header row
        writer.writerows(samples)         # Write data rows
    print(f"Data stored in: {filename}")


def generate_filename(project_name, state):
    """
    Generates a dynamic filename using project name, state number, and current date.

    Parameters:
    project_name (str): Name of the project (e.g., 'DemoProject')
    state (int): Current simulation state
    Returns:
    str: Generated filename
    """
    date_str = datetime.now().strftime("%d.%m.%Y_%H-%M")  # Format date as dd.mm.yyyy.hh-mm
    return f"{project_name}_state{state}_{date_str}.csv"



##################################################################################################################################################
######################################### Initializing the K-Spice Simulator #####################################################################
##################################################################################################################################################

project_path = "C:\K-Spice-Projects\Yggdrasil Hugin LATEST_Eryk_2"  # Path for project folder

timeline = "Yggdrasil_LCS"                        # Name of the timeline to be activated
mdlFile  = "Yggdrasil"                            # Name of the model file to be loaded
prmFile  = "Yggdrasil"                            # Name of the parameter file to be loaded
valFile  = "Yggdrasil_Steady_State_Manual_Mode"   # Name of the initial conditions file to be loaded

# Instantiate the simulator object 
sim = kspice.Simulator(project_path)

#Open the project and load the timeline 
tl = sim.activate_timeline(timeline)

# Load models, parameters, initial_conditions
tl.load(mdlFile, prmFile, valFile)

# initialize the timeline
tl.initialize()

# Different applications 
selected_app = tl.applications[0].name           # Hugin A
selected_app1 = tl.applications[1].name          # Hugin B


# set the execution speed of the timleine to 2.1X real time
tl.set_speed(2.0)

variables = [["D-36L00040A-1200PRd:OutletStream.f","kg/h"],    
             ["D-13HCV2319:TargetPosition","%"],        # Init 100% 
             ["D-13HCV2419:TargetPosition","%"],        # Init 100%
             ["D-13HCV2121A:TargetPosition","%"],       # Init 100%
             ["D-13HCV2121B:TargetPosition","%"],       # Init 100%
             ["D-13HCV0305:TargetPosition","%"],        # Init 55%
             ["F-18FCV0105:TargetPosition","%"],        # Init 18%
             ["N-18FCV0105_RD1:TargetPosition","%"],    # Init 28%
             ["N-18FCV0105_LF1:TargetPosition","%"],    # Init 29%
             ["G-13HCV0505:TargetPosition","%"],        # Init 39%                # Hugin B, ERROR, While loading the model selected_app1, the variables from Hugin A are not loaded 
             ["D-27PIC0101:InternalSetpoint","barg"],   # Init 20.50 barg
             ["D-27TIC0106:InternalSetpoint","C"],      # Init 30 C
             ["D-24PIC0002:InternalSetpoint","barg"],   # Init 75.9 barg
             ["D-26PIC0056:InternalSetpoint","barg"],   # Init 249.0 barg
             ["D-20PIC0304:InternalSetpoint","barg"],   # Init 0.500 barg         # End of controlled 

             # Start of oil export 
             ["D-21L00007A-1400PL-BD20a:OutletStream.f","kg/h"],                  # CRUDE OIL metering MASS FLOW      
             ["D-21L00007A-1400PL-BD20a:OutletStream.q","m3/h"],                  # CRUDE OIL metering Volume FLOW
             ["D-21L00007A-1400PL-BD20a:OutletStream.w","kg/mol"],                # CRUDE OIL Molar mass

             ]    
samples = []

##################################################################################################################################################
######################################### Running the Switch case logic ##########################################################################
##################################################################################################################################################

# Creating a state variable to control the switch case logic
state = 0 
print("Starting the simulation...")

while (True):

    match state:
        case 0: # Initial state 
            print("State 0: Mission starting...")

            # Run the simulation for 60 minutes and collect samples
            run_and_sample(tl, selected_app, variables, 1440, samples)

            # Save the samples to a CSV file        
            filename = generate_filename("Oscillator", state)
            save_samples_to_csv(filename)
            samples.clear()

            break  # Exit the loop 


