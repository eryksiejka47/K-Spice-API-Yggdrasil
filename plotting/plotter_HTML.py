import pandas as pd
import plotly.graph_objects as go

# === 1. Reading data ===
df = pd.read_csv("D20TIC0188_state4_25.07.2025_18-43.csv")

# === 2. Prepare time and list columns ===
time = df.iloc[:, 0]
data_columns = df.columns[1:]
print("Available Columns:")
for i, col in enumerate(data_columns):
    print(f"{i}: {col}")

# === 3. Get user input for column selection ===
user_input = input("Enter column indices to plot (e.g. 0,2:5): ")
def parse_indices(s):
    idx = set()
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        if ':' in part:
            a, b = map(int, part.split(':'))
            idx.update(range(a, b+1))
        else:
            idx.add(int(part))
    return sorted(idx)

selected = parse_indices(user_input)
selected_columns = [data_columns[i] for i in selected]

# === 4. Group columns by unit ===
unit_groups = {}
for col in selected_columns:
    if "[" in col and "]" in col:
        unit = col.split("[")[-1].split("]")[0].strip()
    else:
        unit = "unknown"
    unit_groups.setdefault(unit, []).append(col)

# === 5. Add traces to the figure ===
fig = go.Figure()
color_pool = [
    "#1f77b4", "#ff7f0e", "#217021", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#e7e724", "#17becf",
    "#00090a", "#5fee33", "#fcba03", "#a14ba0"
]
color_index = 0
yaxis_count = 1
yaxis_map = {}

for unit, cols in unit_groups.items():
    axis_id  = 'y'  if yaxis_count == 1 else f'y{yaxis_count}'
    axis_key = 'yaxis' if axis_id == 'y' else f'yaxis{axis_id[1:]}'
    yaxis_map[unit] = (axis_id, axis_key)
    for col in cols:
        fig.add_trace(go.Scatter(
            x=time,
            y=df[col],
            mode='lines+markers',
            name=col,
            marker=dict(color=color_pool[color_index % len(color_pool)]),
            yaxis=axis_id
        ))
        color_index += 1
    yaxis_count += 1

# === 6. Base layout ===
layout = dict(
    title="D20TIC0188: 10% Downstep",
    xaxis=dict(title=df.columns[0]),
    hovermode='x unified',
    width=1400,
    height=700
)

# === 7. Configure axes with overlaying and fractional position ===
left_count = 0
right_count = 0

for i, (unit, (axis_id, axis_key)) in enumerate(yaxis_map.items()):
    side = 'left' if i % 2 == 0 else 'right'
    axis_cfg = dict(
        title=dict(text=unit, font=dict(color=color_pool[i % len(color_pool)])),
        anchor='x',
        side=side,
        showgrid=False,
        tickfont=dict(color=color_pool[i % len(color_pool)]),
        autorange=True
    )
    if axis_id != 'y':
        axis_cfg['overlaying'] = 'y'
    if side == 'left':
        axis_cfg['position'] = left_count * 0.05
        left_count += 1
    else:
        axis_cfg['position'] = 1 - right_count * 0.05
        right_count += 1

    layout[axis_key] = axis_cfg

fig.update_layout(layout)

# === 8. Save to HTML with user-defined filename ===

output_filename = input("Enter filename to save the interactive chart (e.g. chart.html): ")
if not output_filename.lower().endswith('.html'):
    output_filename += '.html'
fig.write_html(output_filename)
print(f"✅ Ready! Automatically saved as '{output_filename}'")
