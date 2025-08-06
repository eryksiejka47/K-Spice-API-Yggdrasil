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
        ["D-36L00040A-1200PRd:MassFlow",                    "kg/h"],          # 13050-01 FULLA PRODUCTION FLOWLINE                        0
        ["F1_pf04:OutletStream.f",                          "kg/h"],          # 18011-01- F1                                              1
        ["F3_pf04:OutletStream.f",                          "kg/h"],          # 18011-01- F3                                              2
        ["F6_pf04:OutletStream.f",                          "kg/h"],          # 18011-01- F6                                              3
        ["D-20L02001A-1600PR:OutletStream.f",               "kg/h"],          # 20070-01 HP Separator                                     4
        ["D-20VA006:Pressure",                              "barg"],          # 20070-01 HP Separator                                     5

        ["LedaBoundary_Rind_pv:OutletStream[0].f",          "kg/h"],          # 13040-01 RIND Production Flowline                         6
        ["RD1_pf04:OutletStream.f",                         "kg/h"],          # 18051-01 RD1                                              7
        ["RD2_pf04:OutletStream.f",                         "kg/h"],          # 18051-01 RD2                                              8
        ["RD3_pf04:OutletStream.f",                         "kg/h"],          # 18051-01 RD3 (RDSLG)                                      9
        ["D-13L00103A-1400PRb:MassFlow",                    "kg/h"],          # From Manifold RIND to Main Production Manifold           10
        ["D-13L00104A-1400PRa_pv:OutletStream[0].f",        "kg/h"],          # From Manifold RIND to Main Test Manifold                 11

        ["LedaBoundary_Langfjellet_pv:OutletStream[0].f",   "kg/h"],          # 13045-01 LANGFJELLET Production Flowline                 12
        ["LF1_pf04:OutletStream.f",                         "kg/h"],          # 18051-01 LF1                                             13
        ["LF2_pf04:OutletStream.f",                         "kg/h"],          # 18051-01 LF2                                             14
        ["LF4_pf04:OutletStream.f",                         "kg/h"],          # 18051-01 LF04b5                                          15
        ["D-13L00203A-1400PRb:MassFlow",                    "kg/h"],          # From Manifold LANGFJELLET to Main Production Manifold    16
        ["D-13L00204A-1400PRa_pv:OutletStream[0].f",        "kg/h"],          # From Manifold LANGFJELLET to Main Test Manifold          17

        ["N-18L8100A-1200PRa_pv:OutletStream[0].f",         "kg/h"],          # 18050-01 LANGFJELLET SOUTH FLOWLINE                      18
        ["LF3_pf04:OutletStream.f",                         "kg/h"],          # 18051-01 LF3                                             19

        ["D-20VA001:Pressure",                              "barg"],          # Main Separator Pressure                                  20             

        #MAIN SEPARATOR
        ["D-20LIC0106:Measurement",                            "m"],          # D-20LIC106  PV                                           21
        ["D-20LIC0106:InternalSetpoint",                       "m"],          # D-20LIC106  SP                                           22
        ["D-20LIC0106:ControllerOutput",                       "%"],          # D-20LIC106  CV                                           23

        ["D-20LIC0119:Measurement",                            "m"],          # D-20LIC0119 PV                                           24
        ["D-20LIC0119:InternalSetpoint",                       "m"],          # D-20LIC0119 SP                                           25
        ["D-20LIC0119:ControllerOutput",                       "%"],          # D-20LIC0119 CV                                           26

        #HP SEPARATOR 
        ["D-20LIC2604:Measurement",                            "m"],          # D-20LIC2604 PV                                           27
        ["D-20LIC2604:InternalSetpoint",                       "m"],          # D-20LIC2604 SP                                           28
        ["D-20LIC2604:ControllerOutput",                       "%"],          # D-20LIC2604 CV                                           29

        ["D-20LIC2627:Measurement",                            "m"],          # D-20LIC2627 PV                                           30
        ["D-20LIC2627:InternalSetpoint",                       "m"],          # D-20LIC2627 SP                                           31
        ["D-20LIC2627:ControllerOutput",                       "%"],          # D-20LIC2627 CV                                           32

        #FRØY SEPARATOR 
        ["D-20LIC2106:Measurement",                            "m"],          # D-20LIC2106 PV                                           33
        ["D-20LIC2106:InternalSetpoint",                       "m"],          # D-20LIC2106 SP                                           34
        ["D-20LIC2106:ControllerOutput",                       "%"],          # D-20LIC2106 CV                                           35

        ["D-20LIC2120:Measurement",                            "m"],          # D-20LIC2120 PV                                           36
        ["D-20LIC2120:InternalSetpoint",                       "m"],          # D-20LIC2120 SP                                           37
        ["D-20LIC2120:ControllerOutput",                       "%"],          # D-20LIC2120 CV                                           38

        #2ND STAGE SEPARATOR 
        ["D-20LIC0206:Measurement",                            "m"],          # D-20LIC0206 PV                                           39
        ["D-20LIC0206:InternalSetpoint",                       "m"],          # D-20LIC0206 SP                                           40
        ["D-20LIC0206:ControllerOutput",                       "%"],          # D-20LIC0206 CV                                           41

        ["D-20LIC0224:Measurement",                            "m"],          # D-20LIC0224 PV                                           42
        ["D-20LIC0224:InternalSetpoint",                       "m"],          # D-20LIC0224 SP                                           43
        ["D-20LIC0224:ControllerOutput",                       "%"],          # D-20LIC0224 CV                                           44

        #3RD STAGE SEPARATOR 
        ["D-20LIC0309:Measurement",                            "m"],          # D-20LIC0309 PV                                           45
        ["D-20LIC0309:InternalSetpoint",                       "m"],          # D-20LIC0309 SP                                           46
        ["D-20LIC0309:ControllerOutput",                    "m3/h"],          # D-20LIC0309 CV                                           47
]

    project_name = "Yggdrasil_tetser"
    chunk_size   = 300
    state        = 0


##################################################################################################################################################
######################################### Running the Switch case logic ##########################################################################
##################################################################################################################################################

print("=== Starting buffered switch-case simulation ===")

    # Loop through states as experiments
while True:
        try:
            match state:
                case 0:
                    # State 0: 2min, adjust valve, 180min
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 0 ---")
                    run_buffered_simulation(tl, app0, variables, 2,   chunk_size, filename)
                    adjust_parameter(tl, app0, "D-13HCV2627:TargetPosition", 1.1)
                    run_buffered_simulation(tl, app1, variables, 180, chunk_size, filename)
                    state = 1

                case 1:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 1 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 1,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-27PIC0101:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 1, chunk_size, filename)
                    state = 2

                case 2:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 2 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 1,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-27TIC0106:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 1, chunk_size, filename)
                    state = 3

                case 3:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 3 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 1,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-24PIC0002:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 1, chunk_size, filename)
                    state = 4

                case 4:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 4 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 1,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-26PIC0056:InternalSetpoint", 1.1)
                    run_buffered_simulation(tl, app0, variables, 11, chunk_size, filename)
                    state = 5

                case 5:
                    filename = generate_filename(project_name, state)
                    print("\n--- STATE 5 ---")
                    tl.load("Yggdrasil", "Yggdrasil", "Yggdrasil_Steady_State_Manual_Mode")
                    tl.initialize()
                    run_buffered_simulation(tl, app0, variables, 1,  chunk_size, filename)
                    adjust_parameter(tl, app0, "D-20PIC0304:InternalSetpoint", 0.9)
                    run_buffered_simulation(tl, app0, variables, 1, chunk_size, filename)
                    print("\n=== Simulation complete! ===")
                    break

        except Exception as e:
            print(f"[FATAL] Interrupted in state {state}: {e!r}")
            break
