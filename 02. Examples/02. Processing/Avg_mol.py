import pandas as pd

# Input and output file names
input_file = "Yggdrasil_state0_07.07.2025_18-23_D_13HCV2627TargetPosition.csv"
output_file = "Yggdrasil_state0_07.07.2025_18-23_D_13HCV2627TargetPosition_upgraded.csv"

###################################################################################################################################################################################################################
################################################################################################ Molar mass maps ##################################################################################################
###################################################################################################################################################################################################################

# Define molar masses for each chemical
chemical_masses = {
    "H2O": 18.015,
    "CO2": 44.01,
    "C6H6": 78.11,
    "NaCl": 58.44,
    "CH4": 16.04,
    "NH3": 17.03,
    "O2": 32.00,
    "N2": 28.02
}

chemical_masses_oil = {
    "H2O": 18.01528,
    "MEG": 62.068,
    "N2": 28.0134,
    "CO2": 44.0095,
    "H2S": 34.08088,
    "C1": 16.04246,
    "C2": 30.06904,
    "C3": 44.097,
    "IC4": 58.1222,
    "NC4": 58.1222,
    "IC5": 72.1514,
    "NC5": 72.1514,
    "NC6": 86.1806,
    "C7FU": 88.41,
    "C7LI-C7FG": 47,
    "C8FU": 101.709,
    "C8LI-C8FG": 47,
    "C9LI-C9FG": 47,
    "C10F-C13R": 47,
    "C11-C12LF": 47,
    "C10C-C15L": 47,
    "C14-C20RD": 229.3099,
    "C18C-C21L": 47,
    "C23-C29RD": 47,
    "C26-C30LF": 386.38,
    "C30-C36LF": 47,
    "C28C-C80R": 47,
    "C39-C80LF": 47,
    "C46-C42C2": 47,
    "C63-C80FR": 691.1777588
}

chemical_masses_gas = {
    "H2O": 18.01528,
    "MEG": 62.068,
    "TEG": 150.18,
    "N2": 28.0134,
    "CO2": 44.0095,
    "H2S": 34.08088,
    "C1": 16.04246,
    "C2": 30.06904,
    "C3": 44.097,
    "IC4": 58.1222,
    "NC4": 58.1222,
    "IC5": 72.1514,
    "NC5": 72.1514,
    "NC6": 86.1806,
    "C7FU": 88.41,
    "C7LI-C7FG": 47,
    "C8FU": 101.709,
    "C8LI-C8FG": 47,
    "C9LI-C9FG": 47,
    "C10F-C13R": 47,
    "C11-C12LF": 47,
    "C10C-C15L": 47,
    "C14-C20RD": 229.3099,
    "C18C-C21L": 47,
    "C23-C29RD": 47,
    "C26-C30LF": 386.38,
    "C30-C36LF": 47,
    "C28C-C80R": 47,
    "C39-C80LF": 47,
    "C46-C42C2": 47,
    "C63-C80FR": 691.1777588
}

###################################################################################################################################################################################################################
################################################################################################ Processing #######################################################################################################
###################################################################################################################################################################################################################

chemicals = list(chemical_masses_oil.keys())                  #CHANGE HERE TO SWAP THE "MAP"
molar_masses = [chemical_masses_oil[ch] for ch in chemicals]  #CHANGE HERE TO SWAP THE "MAP"

# Read the CSV file
try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")
    exit(1)
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

# Display available columns
print("Available columns:")
for i, col in enumerate(df.columns):
    print(f"  {i}: {col}")

# Parse user input for column indices
def parse_indices(input_str):
    indices = []
    for part in input_str.split(','):
        part = part.strip()
        if ':' in part:
            try:
                start, end = map(int, part.split(':'))
                indices.extend(range(start, end + 1))
            except ValueError:
                print(f"Invalid range: {part}")
        elif part:
            try:
                indices.append(int(part))
            except ValueError:
                print(f"Invalid index: {part}")
    return indices

# Get user input
user_input = input("\nEnter column indices for MW calculation (e.g. 0,1,3:5): ")
selected_indices = parse_indices(user_input)

new_column_name = input("Enter the name of the new column: ")

# Check if number of selected columns exceeds available molar masses
if len(selected_indices) > len(molar_masses):
    print(f"Warning: You selected {len(selected_indices)} columns, but only {len(molar_masses)} molar masses are defined.")
    print("Truncating to match available molar masses.")
    selected_indices = selected_indices[:len(molar_masses)]

# Calculate weighted molar mass
total = pd.Series(0.0, index=df.index)

print("\nMapping columns to chemicals:")
for i, idx in enumerate(selected_indices):
    if idx < 0 or idx >= len(df.columns):
        print(f"Index {idx} is out of range (0–{len(df.columns)-1}). Skipping.")
        continue
    col_name = df.columns[idx]
    mw = molar_masses[i]
    chem = chemicals[i]
    print(f"  Column {idx} ({col_name}) → {chem} (MW={mw})")
    try:
        total += (df[col_name] / 100) * mw  
    except Exception as e:
        print(f"Error processing column '{col_name}': {e}")

# Add new column and save to file
df[new_column_name] = total
try:
    df.to_csv(output_file, index=False)
    print(f"\nFile saved successfully as: {output_file}")
except Exception as e:
    print(f"Error saving file: {e}")
    exit(1)

# Display updated headers
print("Updated column headers:")
for col in df.columns:
    print(" ", col)

