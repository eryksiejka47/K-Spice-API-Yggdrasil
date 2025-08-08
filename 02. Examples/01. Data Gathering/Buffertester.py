# Importing necessary libraries
import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
import csv
import kspice

# -----------------------------------------------------------------------------
# Module: Buffered Switch-Case Simulation
# Description: Runs K-Spice simulations in sequential states, adjusting parameters
#              between runs, and writes results to separate CSV files using a
#              chunked buffer strategy to minimize data loss on failure.
# -----------------------------------------------------------------------------

##################################################################################################################################################
############################################################ Functions ###########################################################################
##################################################################################################################################################


# --- CSV Buffering Helpers ---
def _write_header_if_needed(filename, variables):
    """
    Write the CSV header if the file does not exist or is empty.

    Params:
        filename (str): Path to the CSV file.
        variables (List[List[str, str]]): List of [name, unit] pairs for columns.
    """
    try:
        with open(filename, 'r', newline='') as f:
            # If file already has content, skip writing header
            if f.read(1):
                return
    except FileNotFoundError:
        # File does not exist -> will write header
        pass

    header = [['ModelTime', 's']] + variables
    # Flatten header to "Name [unit]" format
    header_flat = [f"{var[0]} [{var[1]}]" for var in header]
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header_flat)


def _flush_buffer(filename, buffer):
    """
    Append all rows in the buffer to the CSV file and clear the buffer.

    Params:
        filename (str): Path to the CSV file.
        buffer (List[List[float]]): Rows to flush to disk.
    """
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(buffer)
    # Caller should clear buffer after flush


def run_buffered_simulation(timeline, app, variables, minutes, chunk_size, filename):
    """
    Run a chunked simulation for a given duration, writing results in increments
    to CSV to avoid data loss on errors or process termination.

    Params:
        timeline (kspice.Timeline): Active K-Spice timeline object.
        app (str): Application name within the timeline.
        variables (List[List[str, str]]): Variables to sample ([name, unit]).
        minutes (int): Simulation duration in minutes.
        chunk_size (int): Number of samples to buffer before writing.
        filename (str): Output CSV file path.
    """
    total_seconds = minutes * 60
    buffer = []

    # Progress checkpoints at 25%, 50%, 75%, 100%
    checkpoints = [
        int(total_seconds * 0.25),
        int(total_seconds * 0.50),
        int(total_seconds * 0.75),
        total_seconds
    ]
    next_cp = 0

    # Ensure CSV header is present
    _write_header_if_needed(filename, variables)
    print(f"Starting {minutes}min simulation (chunk {chunk_size}) → {filename}")

    try:
        for sec in range(1, total_seconds + 1):
            # Advance simulation by one second
            timeline.run_for(timedelta(seconds=1))
            # Sample variables and prepend model time
            sample = timeline.get_values(app, variables)
            sample.insert(0, timeline.model_time.total_seconds())
            buffer.append(sample)

            # Flush to disk if buffer is full
            if len(buffer) >= chunk_size:
                _flush_buffer(filename, buffer)
                buffer.clear()

            # Print progress at defined checkpoints
            if next_cp < len(checkpoints) and sec == checkpoints[next_cp]:
                print(f"  Progress {25 * (next_cp + 1)}%...")
                next_cp += 1

        # Final flush of any remaining rows
        if buffer:
            _flush_buffer(filename, buffer)
            buffer.clear()

        print(f"Completed {minutes}min simulation → data in {filename}")

    except Exception as e:
        # On error, flush what's left, log, then re-raise
        if buffer:
            _flush_buffer(filename, buffer)
        print(f"[ERROR] Simulation failed: {e!r}")
        print(f"Partial data flushed to {filename}")
        raise


# --- Parameter Adjustment Helper ---
def adjust_parameter(timeline, app, parameter_name, multiplier):
    """
    Multiply a control parameter by a given factor and update the timeline.

    Params:
        timeline (kspice.Timeline): Active timeline object.
        app (str): Application name.
        parameter_name (str): Name of the parameter to adjust.
        multiplier (float): Factor to multiply the current value by.
    """
    current = timeline.get_value(app, parameter_name)
    new_val = current * multiplier
    timeline.set_value(app, parameter_name, new_val)
    print(f"Adjusted {parameter_name}: {current} → {new_val} ({multiplier*100:.1f}%)")


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


# --- Filename Generator ---
def generate_filename(project_name, state):
    """
    Create a filename with project name, state index, and timestamp.

    Params:
        project_name (str): Base name for the project.
        state (int): Simulation state index.

    Returns:
        str: Generated filename.
    """
    ts = datetime.now().strftime("%d.%m.%Y_%H-%M")
    return f"{project_name}_state{state}_{ts}.csv"


##################################################################################################################################################
######################################### Initializing the K-Spice Simulator #####################################################################
##################################################################################################################################################


# --- Main Simulation Flow ---
if __name__ == "__main__":
    # Initialize simulator
    project_path = r"C:\K-Spice-Projects\Yggdrasil Hugin LATEST_Eryk_2"
    sim = kspice.Simulator(project_path)
    tl  = sim.activate_timeline("Yggdrasil_LCS")
    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
    tl.initialize()
    tl.set_speed(2.0)

    # Application names
    app0 = tl.applications[0].name  # Hugin A
    app1 = tl.applications[1].name  # Hugin B

    # Variables to sample: [name, unit]
    variables = [
        # Start of oil export 
        ["D-21L00007A-1400PL-BD20a:OutletStream.f","kg/h"],                   # CRUDE OIL metering MASS FLOW                          0
        ["D-21L00007A-1400PL-BD20a:OutletStream.q","m3/h"],                   # CRUDE OIL metering Volume FLOW                        1
        ["D-21L00007A-1400PL-BD20a:OutletStream.w","kg/mol"],                 # CRUDE OIL Molar mass                                  2

        # Start of gas export
        ["D-27L00022A-1400PVd_pv:OutletStream[0].f","kg/h"],                  # GAS EXPORT MASS FLOW                                  3
        ["D-27L00022A-1400PVd_pv:OutletStream[0].q","m3/h"],                  # GAS EXPORT Volume FLOW                                4
        ["D-27L00022A-1400PVd_pv:OutletStream[0].w","kg/mol"],                # GAS EXPORT Molar mass                                 5
        ["D-27PT0260:MeasuredValue","barg"],                                  # Gas export pressure                                   6

        # Active Powers
        ["D-23KA001_m:ActivePower","kW"],                                    # Start of power consumption compressors                 7
        ["D-27KA001_m:ActivePower","kW"],                                    #                                                        8
        ["D-27KA002_m:ActivePower","kW"],                                    #                                                        9                     
        ["D-26KA001_m:ActivePower","kW"],                                    # End of power consumption compressors                  10

        ["D-21PA001A_m:ActivePower","kW"],                                   # Start of power consumption pumps                      11
        ["D-21PA002A_m:ActivePower","kW"],                                   #                                                       12
        ["D-21PA002B_m:ActivePower","kW"],                                   #                                                       13
        ["D-21PA001B_m:ActivePower","kW"],                                   # End of power consumption pumps                        14

        # Pressure measurements  
        ["D-13PT2625:MeasuredValue","barg"],                                 # Upstream Fulla and Lille-FRIGG                        15
        ["D-13PT2628:MeasuredValue","barg"],                                 # Downstream Fulla and Lille-FRIGG                      16

        ["D-13PT2317:MeasuredValue","barg"],                                 # Upstream Rind                                         17
        ["D-13PT2321:MeasuredValue","barg"],                                 # Downstream Rind                                       18

        ["D-13PT2417:MeasuredValue","barg"],                                 # Upstream Langfjellet                                  19
        ["D-13PT2421:MeasuredValue","barg"],                                 # Downstream Langfjellet                                20

        ["D-13PT2118:MeasuredValue","barg"],                                 # Upstream Hugin B (Frøy)                               21
        ["D-13PT2122:MeasuredValue","barg"],                                 # Downstream Hugin B (Frøy)                             22

        #MAIN SEPARATOR
        ["D-20LIC0106:Measurement",                            "m"],         # D-20LIC106  PV                                        23
        ["D-20LIC0106:InternalSetpoint",                       "m"],         # D-20LIC106  SP                                        24
        ["D-20LIC0106:ControllerOutput",                       "%"],         # D-20LIC106  CV                                        25

        ["D-20LIC0119:Measurement",                            "m"],         # D-20LIC0119 PV                                        26
        ["D-20LIC0119:InternalSetpoint",                       "m"],         # D-20LIC0119 SP                                        27
        ["D-20LIC0119:ControllerOutput",                       "%"],         # D-20LIC0119 CV                                        28

        #HP SEPARATOR 
        ["D-20LIC2604:Measurement",                            "m"],         # D-20LIC2604 PV                                        29
        ["D-20LIC2604:InternalSetpoint",                       "m"],         # D-20LIC2604 SP                                        30
        ["D-20LIC2604:ControllerOutput",                       "%"],         # D-20LIC2604 CV                                        31

        ["D-20LIC2627:Measurement",                            "m"],         # D-20LIC2627 PV                                        32
        ["D-20LIC2627:InternalSetpoint",                       "m"],         # D-20LIC2627 SP                                        33
        ["D-20LIC2627:ControllerOutput",                       "%"],         # D-20LIC2627 CV                                        34

        #FRØY SEPARATOR 
        ["D-20LIC2106:Measurement",                            "m"],         # D-20LIC2106 PV                                        35
        ["D-20LIC2106:InternalSetpoint",                       "m"],         # D-20LIC2106 SP                                        36
        ["D-20LIC2106:ControllerOutput",                       "%"],         # D-20LIC2106 CV                                        37

        ["D-20LIC2120:Measurement",                            "m"],         # D-20LIC2120 PV                                        38
        ["D-20LIC2120:InternalSetpoint",                       "m"],         # D-20LIC2120 SP                                        39
        ["D-20LIC2120:ControllerOutput",                       "%"],         # D-20LIC2120 CV                                        40

        #2ND STAGE SEPARATOR 
        ["D-20LIC0206:Measurement",                            "m"],         # D-20LIC0206 PV                                        41
        ["D-20LIC0206:InternalSetpoint",                       "m"],         # D-20LIC0206 SP                                        42
        ["D-20LIC0206:ControllerOutput",                       "%"],         # D-20LIC0206 CV                                        43

        ["D-20LIC0224:Measurement",                            "m"],         # D-20LIC0224 PV                                        44
        ["D-20LIC0224:InternalSetpoint",                       "m"],         # D-20LIC0224 SP                                        45
        ["D-20LIC0224:ControllerOutput",                       "%"],         # D-20LIC0224 CV                                        46

        #3RD STAGE SEPARATOR 
        ["D-20LIC0309:Measurement",                            "m"],         # D-20LIC0309 PV                                        47
        ["D-20LIC0309:InternalSetpoint",                       "m"],         # D-20LIC0309 SP                                        48
        ["D-20LIC0309:ControllerOutput",                    "m3/h"],         # D-20LIC0309 CV                                        49

################################################################################################################################################################

        #21PIC0557
        ["D-21PIC0557:Measurement",                         "barg"],         # D-21PIC0557 PV                                        50
        ["D-21PIC0557:InternalSetpoint",                    "barg"],         # D-21PIC0557 SP                                        51
        ["D-21PIC0557:ControllerOutput",                       "%"],         # D-21PIC0557 CV                                        52
        
        #27TIC0307
        ["D-27TIC0307:Measurement",                            "C"],         # D-27TIC0307 PV                                        53
        ["D-27TIC0307:InternalSetpoint",                       "C"],         # D-27TIC0307 SP                                        54
        ["D-27TIC0307:ControllerOutput",                       "%"],         # D-27TIC0307 CV                                        55

        #23TIC0204
        ["D-23TIC0204:Measurement",                            "C"],         # D-23TIC0204 PV                                        56
        ["D-23TIC0204:InternalSetpoint",                       "C"],         # D-23TIC0204 SP                                        57
        ["D-23TIC0204:ControllerOutput",                       "%"],         # D-23TIC0204 CV                                        58

        #24TIC0008
        ["D-24TIC0008:Measurement",                            "C"],         # D-24TIC0008 PV                                        59
        ["D-24TIC0008:InternalSetpoint",                       "C"],         # D-24TIC0008 SP                                        60
        ["D-24TIC0008:ControllerOutput",                       "%"],         # D-24TIC0008 CV                                        61

        #20TIC0188_S
        ["D-20TIC0188:Measurement",                          "C"],         # D-20TIC0188_S PV                                      62
        ["D-20TIC0188:InternalSetpoint",                     "C"],         # D-20TIC0188_S SP                                      63
        ["D-20TIC0188:ControllerOutput",                     "%"],         # D-20TIC0188_S CV                                      64

        #21TIC0406
        ["D-21TIC0406:Measurement",                            "C"],         # D-21TIC0406 PV                                        65
        ["D-21TIC0406:InternalSetpoint",                       "C"],         # D-21TIC0406 SP                                        66
        ["D-21TIC0406:ControllerOutput",                       "%"],         # D-21TIC0406 CV                                        67

        #21TIC0405
        ["D-21TIC0405:Measurement",                         "C"],         # D-21TIC0405_SP PV                                     68
        ["D-21TIC0405:InternalSetpoint",                    "C"],         # D-21TIC0405_SP SP                                     69
        ["D-21TIC0405:ControllerOutput",                    "%"],         # D-21TIC0405_SP CV                                     70

        #24TDIC0040
        ["D-24TDIC0040:Measurement",                       "C"],         # D-24TDIC0040_SP PV                                     71
        ["D-24TDIC0040:InternalSetpoint",                  "C"],         # D-24TDIC0040_SP SP                                     72
        ["D-24TDIC0040:ControllerOutput",                  "%"],         # D-24TDIC0040_SP CV                                     73

        #27TIC0204
        ["D-27TIC0204:Measurement",                        "C"],         # D-27TIC0204_SP PV                                      74
        ["D-27TIC0204:InternalSetpoint",                   "C"],         # D-27TIC0204_SP SP                                      75
        ["D-27TIC0204:ControllerOutput",                   "%"],         # D-27TIC0204_SP CV                                      76
]

    project_name = "Yggdrasil_tetser"
    chunk_size   = 500
    state        = 47


##################################################################################################################################################
######################################### Running the Switch case logic ##########################################################################
##################################################################################################################################################

print("=== Starting buffered switch-case simulation ===")

    # Loop through states as experiments
while True:
        try:
            match state:

                case 47:
                    # State 0: 2min, adjust valve, 180min
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE WARM UP ---")
                    run_buffered_simulation(tl, app0, variables, 1,   chunk_size, filename)
                    adjust_parameter(tl, app0, "D-21PIC0557:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app1, variables, 1, chunk_size, filename)
                    state = 0

                case 0:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 0 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-21PIC0557:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    state = 1
                    
                case 1:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 1 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-27TIC0307:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    state = 2

                case 2:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 2 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-23TIC0204:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    state = 3

                case 3:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 3 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-24TIC0008:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    state = 4

                case 4:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 4 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-20TIC0188:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    state = 5

                case 5:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 5 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-21TIC0406:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    print("\n=== Simulation complete! ===")
                    state = 6 

                case 6:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 6 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-21TIC0405:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    state = 7

                case 7:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 7 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-24TDIC0040:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    state = 8
                
                case 8:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 8 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 60,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-27TIC0204:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 180, chunk_size, filename)
                    break

        except Exception as e:
            print(f"[FATAL] Interrupted in state {state}: {e!r}")
            break
