import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("ENTER_NAME_OF_YOUR_FILE.csv")

# Extract time and data columns
time = df[df.columns[0]]
data_columns = df.columns[1:]

# Show available columns
print("Available columns for plotting:")
for i, col in enumerate(data_columns):
    print(f"{i}: {col}")

# >>> SELECT COLUMNS TO PLOT <<<
# Example input: 0,1,2,3:10,14:24,29
user_input = input("Enter the column numbers to plot (e.g., 0,1,2,3:10,14:24,29): ")

# Parse the input into a list of indices
def parse_indices(input_str):
    indices = set()
    parts = input_str.split(',')
    for part in parts:
        if ':' in part:
            start, end = map(int, part.split(':'))
            indices.update(range(start, end + 1))
        else:
            indices.add(int(part))
    return sorted(indices)

selected_indices = parse_indices(user_input)

# Select columns
selected_columns = [data_columns[i] for i in selected_indices]

# Group selected columns by unit
unit_groups = {}
for col in selected_columns:
    if "[" in col and "]" in col:
        unit = col.split("[")[-1].split("]")[0].strip()
    else:
        unit = "unknown"
    unit_groups.setdefault(unit, []).append(col)

# Create the base plot
fig, host = plt.subplots(figsize=(14, 7))
fig.subplots_adjust(right=0.75, top=0.85)

# Define a pool of visually distinct colors
color_pool = [
    "#1f77b4", "#ff7f0e", "#217021", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#e7e724", "#17becf",
    "#00090a", "#5fee33",
]

# Create additional Y-axes on the left
axes = [host]
for i in range(1, len(unit_groups)):
    ax = host.twinx()
    ax.spines["left"].set_position(("axes", -0.1 * i))
    ax.spines["left"].set_visible(True)
    ax.yaxis.set_label_position("left")
    ax.yaxis.set_ticks_position("left")
    axes.append(ax)

# Plot each group
lines = []
labels = []
color_index = 0
for ax, (unit, cols) in zip(axes, unit_groups.items()):
    for col in cols:
        color = color_pool[color_index % len(color_pool)]
        color_index += 1
        line, = ax.plot(time, df[col], label=col, color=color)
        lines.append(line)
        labels.append(col)
    ax.set_ylabel(unit)

# X-axis label
host.set_xlabel(df.columns[0])

# Legend at the top
fig.legend(lines, labels, loc='upper center', ncol=3, bbox_to_anchor=(0.5, 0.98))

# Final styling
plt.title("NAME_OF_YOUR_PLOT")
plt.grid(True)
plt.tight_layout()
plt.show()
