import csv
import json
from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent

with (BASE_DIR / 'yield_measured.csv').open(encoding='utf-8-sig', newline='') as source:
    measurements = list(csv.DictReader(source))

# Match each plot and treatment to its simulation output
simulation_paths = {}
for config_path in (BASE_DIR / 'sim_files').glob('sim*.json'):
    with config_path.open(encoding='utf-8') as source:
        config = json.load(source)
    plot_no = 12000 + int(Path(config['site.json']).stem.split('_')[-1])
    crop = Path(config['crop.json']).stem
    treatment = 10 if crop == 'crop_ref' else int(crop.split('_')[-1])
    simulation_paths[plot_no, treatment] = BASE_DIR / 'output' / f'{config_path.stem}.csv'

# Read simulated harvest yields for the measured plots and years
simulated = {}
simulated_crops = {}
for pair in {(int(row['plot_no']), int(row['treatment'])) for row in measurements}:
    with simulation_paths[pair].open(encoding='utf-8', newline='') as source:
        rows = csv.reader(source, delimiter=';')
        for row in rows:
            if row == ['crop']:
                break
        else:
            raise ValueError(f'No crop section in {simulation_paths[pair]}')
        header = next(rows)
        for _ in range(3):  # Skip units and aggregation metadata
            next(rows)
        needed_years = {
            row['year'] for row in measurements
            if (int(row['plot_no']), int(row['treatment'])) == pair
        }
        for row in csv.DictReader(source, fieldnames=header, delimiter=';'):
            if not row['harv-year'] or not row['harv-year'].isdigit():
                break  # End of the crop section
            if row['harv-year'] in needed_years:
                simulated[*pair, row['harv-year']] = float(row['Yield'])
                simulated_crops[*pair, row['harv-year']] = row['Crop']

# Group matched observations and simulations by treatment
plot_data = {}
for row in measurements:
    if row['yield_dm_kg_ha']:
        key = (int(row['plot_no']), int(row['treatment']), row['year'])
        if key in simulated:  # Some simulation years have no harvest output
            plot_data.setdefault(key[1], []).append((float(row['yield_dm_kg_ha']), simulated[key]))

with (BASE_DIR / 'yield_obs_sim.csv').open('w', newline='', encoding='utf-8') as output:
    writer = csv.writer(output)
    writer.writerow(['plot', 'treatment', 'crop', 'obs_yield', 'sim_yield'])
    for row in measurements:
        key = (int(row['plot_no']), int(row['treatment']), row['year'])
        if row['yield_dm_kg_ha'] and key in simulated:
            writer.writerow([key[0], key[1], simulated_crops[key],
                             float(row['yield_dm_kg_ha']), simulated[key]])

values = [value for pairs in plot_data.values() for pair in pairs for value in pair]
padding = max((max(values) - min(values)) * 0.05, 1)
limits = (min(values) - padding, max(values) + padding)
fig, axes = plt.subplots(2, 3, figsize=(13, 8), sharex=True, sharey=True, layout='constrained')

for axis, treatment, color in zip(axes.flat, sorted(plot_data), plt.cm.tab10.colors):
    observed, predicted = zip(*plot_data[treatment])
    axis.scatter(observed, predicted, s=28, alpha=0.7, color=color, edgecolors='white', linewidths=0.35)
    axis.plot(limits, limits, '--', color='black', linewidth=1)
    axis.set(title=f'Treatment {treatment} (n={len(observed)})', xlim=limits, ylim=limits, aspect='equal')
    axis.grid(alpha=0.25)

fig.supxlabel('Observed yield (kg DM/ha)')
fig.supylabel('Simulated yield (kg DM/ha)')
fig.suptitle('Observed vs simulated yield by treatment')
plt.show()
