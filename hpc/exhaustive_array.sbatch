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
#SBATCH --mem=16g
#SBATCH --time=2-00:00:00
#SBATCH --output=logs/exh_%A_%a.out
#SBATCH --array=0-2

# --cpus 14 is REQUIRED for bit-identical results with the local pipeline:
# permuteMeasEq's L'Ecuyer RNG streams are split by worker count.

SCALES=(anhedonic_depression social_anxiety well_being)
SIF=${SIF:-hitop-cfa.sif}
DATA=${DATA:-/data/$USER/hitop}

scale=${SCALES[$SLURM_ARRAY_TASK_ID]}
mkdir -p logs
apptainer exec --bind "$DATA":/data "$SIF" \
  pixi run --manifest-path /opt/hitop/pixi.toml \
  python /opt/hitop/notebooks/run_exhaustive_scale.py "$scale" \
    --num-iter 1000 --cpus 14 \
    --data-dir /data/finaldata --cfa-dir /data/cfa
