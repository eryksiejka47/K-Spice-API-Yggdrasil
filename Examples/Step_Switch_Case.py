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
tl.set_speed(2.1)

variables = [["D-13HCV2627:TargetPosition","%"],                          # Start of controlled 
             ["D-13HCV2319:TargetPosition","%"],  
             ["D-13HCV2419:TargetPosition","%"],
             ["D-13HCV2121A:TargetPosition","%"],
             ["D-13HCV2121B:TargetPosition","%"],  
             ["D-13HCV0305:TargetPosition","%"],
             ["F-18FCV0105:TargetPosition","%"],
             ["N-18FCV0105_RD1:TargetPosition","%"],
             ["N-18FCV0105_LF1:TargetPosition","%"],
             ["G-13HCV0505:TargetPosition","%"],                           # Hugin B
             ["D-27PIC0101:InternalSetpoint","barg"],
             ["D-27TIC0106:InternalSetpoint","C"],
             ["D-24PIC0002:InternalSetpoint","barg"],
             ["D-26PIC0056:InternalSetpoint","barg"],
             ["D-20PIC0304:InternalSetpoint","barg"],                      # End of controlled 

             ["D-21L00007A-1400PL-BD20a:OutletStream.f","kg/h"],           # Start of oil export 
             ["D-21L00007A-1400PL-BD20a:OutletStream.q","m3/h"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[0]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[1]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[2]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[3]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[4]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[5]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[6]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[7]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[8]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[9]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[10]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[11]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[12]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[13]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[14]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[15]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[16]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[17]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[18]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[19]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[20]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[21]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[22]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[23]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[24]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[25]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[26]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[27]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[28]","%"],
             ["D-21L00007A-1400PL-BD20a:OutletStream.x[29]","%"],        # End of oil export

             ["D-21L00007A-1400PL-BD20a:OutletStream.w","kg/mol"],       # Molar mass of oil export

             ["D-27L00022A-1400PVd_pv:OutletStream[0].f","kg/h"],        # Start of gas export
             ["D-27L00022A-1400PVd_pv:OutletStream[0].q","m3/h"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[0]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[1]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[2]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[3]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[4]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[5]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[6]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[7]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[8]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[9]","%"],       
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[10]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[11]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[12]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[13]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[14]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[15]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[16]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[17]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[18]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[19]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[20]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[21]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[22]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[23]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[24]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[25]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[26]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[27]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[28]","%"],
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[29]","%"],      
             ["D-27L00022A-1400PVd_pv:OutletStream[0].x[30]","%"],       # End of gas export 

             ["D-27L00022A-1400PVd_pv:OutletStream[0].w","kg/mol"],      # Molar mass of gas export

             ["D-27PT0260:MeasuredValue","barg"],                        # Gas export pressure

             ["D-23KA001_m:ActivePower","kW"],                           # Start of power consumption compressors
             ["D-27KA001_m:ActivePower","kW"],
             ["D-27KA002_m:ActivePower","kW"],
             ["D-26KA001_m:ActivePower","kW"],                           # End of power consumption compressors

             ["D-21PA001A_m:ActivePower","kW"],                          # Start of power consumption pumps
             ["D-21PA002A_m:ActivePower","kW"],
             ["D-21PA002B_m:ActivePower","kW"],
             ["D-21PA001B_m:ActivePower","kW"],                          # End of power consumption pumps

             ["D-13PT2625:MeasuredValue","barg"],                        # Upstream Fulla and Lille-FRIGG
             ["D-13PT2628:MeasuredValue","barg"],                        # Downstream Fulla and Lille-FRIGG

             ["D-13PT2317:MeasuredValue","barg"],                        # Upstream Rind
             ["D-13PT2321:MeasuredValue","barg"],                        # Downstream Rind

             ["D-13PT2417:MeasuredValue","barg"],                        # Upstream Langfjellet
             ["D-13PT2421:MeasuredValue","barg"],                        # Downstream Langfjellet

             ["D-13PT2118:MeasuredValue","barg"],                        # Upstream Hugin B (Frøy)
             ["D-13PT2122:MeasuredValue","barg"],                        # Downstream Hugin B (Frøy)

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
            print("State 0: Initializing the simulation...")

            # Run the simulation for 60 minutes and collect samples
            run_and_sample(tl, selected_app1, variables, 2, samples)

            # Increase the valve stem position by 10% 
            adjust_parameter(tl, selected_app1, "G-13HCV0505:TargetPosition", 1.1)

            # Run the simulation for 3 hours (180 minutes) and collect samples
            run_and_sample(tl, selected_app1, variables, 3, samples)

            # Save the samples to a CSV file        
            filename = generate_filename("Yggdrasil", state)
            save_samples_to_csv(filename)
            samples.clear()

            # Advance to the next state
            state = 1

        case 1: # Switch case 1
            print("State 1 reached, loading new initial conitions...")

            # Reload model, parameters, and initial conditions
            tl.load(mdlFile, prmFile, valFile)
            tl.initialize()

            # Run the simulation for 60 minutes and collect samples
            run_and_sample(tl, selected_app, variables, 60, samples)

            # Increase the valve stem position by 10% 
            adjust_parameter(tl, selected_app, "D-27PIC0101:InternalSetpoint", 1.1)

            # Run the simulation for 3 hours (180 minutes) and collect samples
            run_and_sample(tl, selected_app, variables, 180, samples)

            # Save the samples to a CSV file        
            filename = generate_filename("Yggdrasil", state)
            save_samples_to_csv(filename)
            samples.clear()
            
            state = 2

        case 2: # Switch case 2
            print("State 2 reached, loading new initial conitions...")

            # Reload model, parameters, and initial conditions
            tl.load(mdlFile, prmFile, valFile)
            tl.initialize()

            # Run the simulation for 60 minutes and collect samples
            run_and_sample(tl, selected_app, variables, 60, samples)

            # Increase the valve stem position by 10% 
            adjust_parameter(tl, selected_app, "D-27TIC0106:InternalSetpoint", 1.1)

            # Run the simulation for 3 hours (180 minutes) and collect samples
            run_and_sample(tl, selected_app, variables, 180, samples)

            # Save the samples to a CSV file        
            filename = generate_filename("Yggdrasil", state)
            save_samples_to_csv(filename)
            samples.clear()

            state = 3   
        
        case 3: # Switch case 3
            print("State 3 reached, loading new initial conitions...")

            # Reload model, parameters, and initial conditions
            tl.load(mdlFile, prmFile, valFile)
            tl.initialize()

            # Run the simulation for 60 minutes and collect samples
            run_and_sample(tl, selected_app, variables, 60, samples)

            # Increase the valve stem position by 10% 
            adjust_parameter(tl, selected_app, "D-24PIC0002:InternalSetpoint", 1.1)

            # Run the simulation for 3 hours (180 minutes) and collect samples
            run_and_sample(tl, selected_app, variables, 180, samples)

            # Save the samples to a CSV file        
            filename = generate_filename("Yggdrasil", state)
            save_samples_to_csv(filename)
            samples.clear()

            state = 4


        case 4: # Switch case 4
            print("State 4 reached, loading new initial conitions...")    

            # Reload model, parameters, and initial conditions
            tl.load(mdlFile, prmFile, valFile)
            tl.initialize()

            # Run the simulation for 60 minutes and collect samples
            run_and_sample(tl, selected_app, variables, 60, samples)

            # Increase the valve stem position by 10% 
            adjust_parameter(tl, selected_app, "D-26PIC0056:InternalSetpoint", 1.1)

            # Run the simulation for 3 hours (180 minutes) and collect samples
            run_and_sample(tl, selected_app, variables, 180, samples)

            # Save the samples to a CSV file        
            filename = generate_filename("Yggdrasil", state)
            save_samples_to_csv(filename)
            samples.clear()

            state = 5
        
        case 5: # Switch case 5
            print("State 5 reached, loading new initial conitions...")  

            # Reload model, parameters, and initial conditions
            tl.load(mdlFile, prmFile, valFile)
            tl.initialize()

            # Run the simulation for 60 minutes and collect samples
            run_and_sample(tl, selected_app, variables, 60, samples)

            # Decrease the valve stem position by 10% 
            adjust_parameter(tl, selected_app, "D-20PIC0304:InternalSetpoint", 1.1) 

            # Run the simulation for 3 hours (180 minutes) and collect samples
            run_and_sample(tl, selected_app, variables, 180, samples)

            # Save the samples to a CSV file        
            filename = generate_filename("Yggdrasil", state)
            save_samples_to_csv(filename)
            samples.clear()

            print("Simulation completed successfully.")
            
            # Exit the loop after completing all states
            break

       
            
