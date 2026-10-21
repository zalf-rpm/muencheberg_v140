# Müncheberg V140 MONICA Setup

This repository contains MONICA simulation inputs for the Müncheberg V140 experiment.

The current setup includes 48 simulations covering six treatment codes (10, 13, 15, 25, 35, and 45), with eight simulations per treatment. All simulations run from 1 January 1963 to 31 December 2024.

## Repository contents

| Path | Purpose |
| --- | --- |
| `sim_files/sim1.json` … `sim48.json` | Simulation configurations linking crop management, site, climate, and output settings. |
| `crop_files/` | Crop definitions and management schedules for the six treatments. |
| `site_files/` | Plot-specific soil profiles and site parameters. |
| `climate_MUE.csv` | Daily weather inputs. |
| `soil_corg_measured.csv` | Measured SOC values, identified by plot, treatment, and sampling date. |
| `yield_measured.csv` | Measured crop yields in kg DM per hectare, identified by plot, treatment, and year. |
| `run_monica.cmd` | Windows batch script that runs every `sim*.json` configuration. |
| `obs_vs_sim_soc.py` | Matches SOC observations to daily simulation results, exports matched values, and plots comparisons by treatment. |
| `obs_vs_sim_yield.py` | Matches yield observations to simulated harvest results, exports matched values, and plots comparisons by treatment. |

## Requirements

- Windows for the supplied batch script.
- A MONICA installation, including `monica-run.exe` and the matching `monica-parameters` directory.
- Python 3.11 or newer and Matplotlib for the comparison scripts.

The MONICA executable and its parameter library are external dependencies and are not included here.

## Run the simulations

1. Open `run_monica.cmd` and update both installation paths to match your MONICA installation:

   ```bat
   set MONICA_PARAMETERS=C:\MONICA\monica_win64_3.6.56.OxygenDeficit_fix\monica-parameters
   ```

   Also update the path to `bin\monica-run.exe` inside the loop. `MONICA_PARAMETERS` supplies the base directory for parameter files referenced by the JSON inputs.

2. Open PowerShell in the repository root and run:

   ```powershell
   .\run_monica.cmd
   ```

The script creates `output/` if necessary and runs all 48 configurations sequentially. Each simulation writes a CSV named after its configuration, such as `output/sim1.csv`.

Inspect MONICA's console output for errors: the batch script prints a completion message even if an individual simulation fails. Rerunning the script targets the same output filenames.

## Data

### Plot and treatment mapping

The site filenames are derived from the plot numbers. For example, `site_7.json` maps to plot 12007 (`12000 + 7`). The crop filenames follow the treatment codes, except for `crop_ref.json`, which corresponds to treatment code 10.

| Crop file | Treatment code | Description |
| --- | --- | --- |
| `crop_ref.json` | 10 | Control. No mineral or organic fertilization; maintenance liming only. |
| `crop_13.json` | 13 | Mineral fertilization (Level 3). Mineral fertilizer levels adjusted according to crop species. P and K fertilization differentiated among treatments until 1993; from 1994 onward, uniform across all treatments. |
| `crop_15.json` | 15 | Mineral fertilization (Level 5). Mineral fertilizer levels adjusted according to crop species. P and K fertilization differentiated among treatments until 1993; from 1994 onward, uniform across all treatments. |
| `crop_25.json` | 25 | Mineral fertilization (Level 5) plus 1.2 t/ha dry matter per year of cattle manure (solid slurry from 1977–1981), equivalent to 0.7 livestock units (LU) per ha. From 1967 to 1982, approximately 1 t/ha manure dry matter per year; from 1983 onward, 1.2 t/ha manure dry matter per year. |
| `crop_35.json` | 35 | Mineral fertilization (Level 5) plus 3.2 t/ha dry matter per year of cattle manure (solid slurry from 1977–1981), equivalent to 1.7 livestock units (LU) per ha. From 1967 to 1982, approximately 3 t/ha manure dry matter per year; from 1983 onward, 3.2 t/ha manure dry matter per year. |
| `crop_45.json` | 45 | Mineral fertilization (Level 5) plus 4 t/ha straw dry matter after cereal crops. Until 1981, 5 t/ha fresh matter; from 1983 onward, generally 4 t/ha dry matter. |

### Comparing SOC measurements with MONICA simulations

The daily output settings request SOC for the upper 0–30 cm of soil. The measurements have a sampling depth of 0–25 cm. To compare the simulations results with the measurements, use the following conversion:

| MONICA result | Measurement | Conversion |
| --- | --- | --- |
| `SOC_0_30_g_m2` | `obs_corg_kg` | g m-2 * 10 = kg ha-1 |
| `SOC_0_30_kgkg` | `obs_c_mg` | kg kg-1 * 100000 = mg 100 g-1 |
| `SOC_0_30_kgkg` | `obs_corg_%` | kg kg-1 * 100 = % |
