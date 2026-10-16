@echo off

set MONICA_PARAMETERS=C:\MONICA\monica_win64_3.6.56.OxygenDeficit_fix\monica-parameters

if not exist "output" mkdir "output"

for %%F in (sim_files\sim*.json) do (
    echo Running simulation: %%F

    "C:\MONICA\monica_win64_3.6.56.OxygenDeficit_fix\bin\monica-run.exe" -o "output\%%~nF.csv" "%%F"

    echo Simulation %%F done.
)

echo All simulations done.