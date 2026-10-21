import csv
import json
from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent

with (BASE_DIR / 'soil_corg_measured.csv').open(encoding='utf-8-sig', newline='') as source:
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

# Read daily simulated SOC only for the measured plots and dates
simulated = {}
for pair in {(int(row['plot_no']), int(row['treatment'])) for row in measurements}:
    with simulation_paths[pair].open(encoding='utf-8', newline='') as source:
        rows = csv.reader(source, delimiter=';')
        for row in rows:
            if row == ['daily']:
                break
        else:
            raise ValueError(f'No daily section in {simulation_paths[pair]}')
        header = next(rows)
        for _ in range(3):  # Skip units and aggregation metadata
            next(rows)
        needed_dates = {
            row['sampling_date'] for row in measurements
            if (int(row['plot_no']), int(row['treatment'])) == pair
        }
        for row in csv.DictReader(source, fieldnames=header, delimiter=';'):
            if row['Date'] in needed_dates:
                simulated[*pair, row['Date']] = float(row['SOC_0_30_kgkg']) * 100

# Group matched observations and simulations by treatment
plot_data = {}
for row in measurements:
    key = (int(row['plot_no']), int(row['treatment']), row['sampling_date'])
    value = simulated[key]
    if row['obs_corg_%']:
        plot_data.setdefault(key[1], []).append((float(row['obs_corg_%']), value))

with (BASE_DIR / 'soc_obs_sim.csv').open('w', newline='', encoding='utf-8') as output:
    writer = csv.writer(output)
    writer.writerow(['plot', 'treatment', 'sampling_date', 'obs_soc', 'sim_soc'])
    for row in measurements:
        key = (int(row['plot_no']), int(row['treatment']), row['sampling_date'])
        if row['obs_corg_%'] and key in simulated:
            writer.writerow([key[0], key[1], key[2], float(row['obs_corg_%']), simulated[key]])

values = [value for pairs in plot_data.values() for pair in pairs for value in pair]
padding = max((max(values) - min(values)) * 0.05, 0.01)
limits = (min(values) - padding, max(values) + padding)
fig, axes = plt.subplots(2, 3, figsize=(13, 8), sharex=True, sharey=True, layout='constrained')

for axis, treatment, color in zip(axes.flat, sorted(plot_data), plt.cm.tab10.colors):
    observed, predicted = zip(*plot_data[treatment])
    axis.scatter(observed, predicted, s=28, alpha=0.7, color=color, edgecolors='white', linewidths=0.35)
    axis.plot(limits, limits, '--', color='black', linewidth=1)
    axis.set(title=f'Treatment {treatment} (n={len(observed)})', xlim=limits, ylim=limits, aspect='equal')
    axis.grid(alpha=0.25)

fig.supxlabel('Observed SOC (%)')
fig.supylabel('Simulated SOC (%)')
fig.suptitle('Observed vs simulated SOC by treatment')
plt.show()
