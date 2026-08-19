#!/bin/bash
# One SLURM array task per scale. EDIT the SCALES list, SIF, and DATA below.
#
# DATA must contain finaldata/ (dat_val.csv, dat_gp_grid1st_full.csv,
# dat_en_grid1st_full.csv) and cfa/ (including the *_history.pkl stepwise
# pickles, which provide the size caps, and any exhaustive_progress_*.pkl
# you want to resume from). Results = cfa/exhaustive_progress_{scale}.pkl;
# copy those back into the local data/cfa/ and rerun the exploratory
# notebook, which short-circuits every completed scale.
#
#SBATCH --job-name=hitop-exh
#SBATCH --cpus-per-task=14
#SBATCH --threads-per-core=1
#SBATCH --mem=16g
#SBATCH --time=2-00:00:00
#SBATCH --output=logs/exh_%A_%a.out
#SBATCH --array=0-2

# --cpus 14 is REQUIRED for bit-identical results with the local pipeline:
# permuteMeasEq's L'Ecuyer RNG streams are split by worker count.
# --threads-per-core=1 makes --cpus-per-task=14 mean 14 PHYSICAL cores
# (no hyperthread sharing), so each of the 14 workers gets a full core;
# worker count is unchanged, so results stay bit-identical.

SCALES=(anhedonic_depression social_anxiety well_being)
SIF=${SIF:-hitop-cfa.sif}
DATA=${DATA:-/data/MLDSST/$USER/hitop/scalar/data}

scale=${SCALES[$SLURM_ARRAY_TASK_ID]}
mkdir -p logs
# no pixi at runtime: source the baked activation and call python directly
# (on Biowulf, /data is auto-bound; the explicit --bind keeps this template
# portable to clusters that do not auto-bind)
apptainer exec --bind "$DATA":"$DATA" "$SIF" bash -c "
  source /opt/hitop/activate.sh
  python /opt/hitop/notebooks/run_exhaustive_scale.py '$scale' \
    --num-iter 1000 --cpus 14 \
    --data-dir '$DATA/finaldata' --cfa-dir '$DATA/cfa'"
