# Running the exhaustive searches on HPC

The per-scale exhaustive searches are independent, resumable, and share
nothing at runtime, so the natural HPC shape is **one SLURM array task
per scale**, each using 14 CPUs for `permuteMeasEq`. The container holds
only the environment + code; data is bind-mounted, and the per-scale
progress pickles are the artifact that moves between HPC and your laptop.

Environment reproducibility: the image is solved from `pixi.lock`
(linux-64 pins verified to match the local pipeline: R 4.2.3, rpy2 3.5.1,
python 3.11) plus pinned R packages (lavaan 0.7-2 from CRAN; the patched
semTools fork `shotgunosine/semTools@db294f2`, i.e. 0.5.8.903, whose
versions are asserted at build time).

## 1. Build the image

Option A — directly on the cluster (no Docker needed), from the repo root:

    module load singularity
    singularity build hitop-cfa.sif hpc/hitop_cfa.def

Option B — anywhere with Docker (note `--platform linux/amd64` when
building on an ARM Mac), then convert:

    docker buildx build --platform linux/amd64 -f hpc/Dockerfile -t hitop-cfa .
    apptainer build hitop-cfa.sif docker-daemon://hitop-cfa:latest

If the cluster disallows local `apptainer build`, check its docs for the
remote builder, or push the Docker image to a registry and
`apptainer build hitop-cfa.sif docker://<registry>/hitop-cfa`.

### Verify the build

Deterministic cross-check against the laptop (same seeds, same worker
count -> same permutation draws). Use your real data path (on Biowulf,
/data/$USER/... is auto-bound into the container):

    apptainer run hitop-cfa.sif run_exhaustive_scale.py insomnia \
        --num-iter 25 --cpus 14 \
        --data-dir /data/MLDSST/$USER/hitop/scalar/data/finaldata --cfa-dir /tmp/check
    # run the identical command locally (pixi run python ...) and compare
    # the printed results dict; they should match. Small borderline
    # discrepancies would indicate BLAS-level numeric differences --
    # re-check with --num-iter 100 before trusting the image.

Nothing invokes pixi at runtime: the image bakes an activation script
(/opt/hitop/activate.sh) at build time and the runscript/entrypoint
sources it and calls the environment's python directly. (Runtime pixi
would try to re-verify the environment, writing caches under $HOME --
which fails on NFS homes -- and would need network, which compute nodes
don't have.)

## 2. Ship the data

The jobs need a data root containing:

    finaldata/   dat_val.csv, dat_gp_grid1st_full.csv, dat_en_grid1st_full.csv
    cfa/         *_history.pkl        (stepwise pickles: provide the size caps)
                 exhaustive_progress_*.pkl   (optional: resume partial searches)

    rsync -av data/finaldata data/cfa cluster:/data/$USER/hitop/

## 3. Run

Edit the `SCALES` array (and `--array` range), `SIF`, and `DATA` in
`hpc/exhaustive_array.sbatch`, then:

    sbatch hpc/exhaustive_array.sbatch

**Keep `--cpus 14` and `--cpus-per-task=14`.** permuteMeasEq's L'Ecuyer
RNG streams are split by worker count, so the permutation p for a given
test is only bit-identical to the local pipeline at 14 workers. More
cores would still be valid tests, just not reproducible against the
laptop runs. The template also sets `--threads-per-core=1`, which makes
the 14 requested CPUs 14 physical cores -- one per worker, no
hyperthread sharing -- without changing the worker count (or the
results).

Search behavior is identical to the exploratory notebook
(`exhaustive_search_scale`): val_gp-first early abandon, the calibrated
parametric delta screen (alpha = .005; configural never screened),
stepwise-certificate size caps, and per-combination progress persistence
-- a preempted or timed-out task resumes exactly where it stopped when
resubmitted.

## 4. Monitor

    apptainer exec -B /data/MLDSST hitop-cfa.sif bash -c \
        "source /opt/hitop/activate.sh && \
         python /opt/hitop/notebooks/exploratory_status.py \
         /data/MLDSST/$USER/hitop/scalar/data/cfa"

plus the per-task SLURM logs in `logs/` (per-combination lines with
abandon/screen reasons).

## 5. Bring results home

Copy the finished progress pickles back into the local `data/cfa/`:

    rsync -av cluster:/data/$USER/hitop/cfa/exhaustive_progress_\*.pkl data/cfa/

then rerun `NB_2_cfa_exploratory.ipynb` (or just its search + parse
cells): every HPC-completed scale short-circuits from its pickle,
re-prints its `!!!!!` result lines into the log, and the parse /
review-note / consolidation pipeline proceeds as if the search had run
locally.

## Notes

- The image bakes a snapshot of `src/` and the two runner scripts; code
  changes require a rebuild (the environment layers are cached, so
  rebuilds are quick).
- BLAS is pinned to 1 thread inside the image (permuteMeasEq provides
  the parallelism); do not raise it.
- `--mem=16g` is generous; the fits are small. `--time`: the capped
  10-item scales are worst-case ~1-2 days at 1000 iters if nothing
  passes until small sizes; resumability makes shorter limits safe too.

## Troubleshooting

- `failed to create uv cache directory ... /home/.../.cache/rattler/...`
  (or any rattler/uv cache error at runtime): you are running an image
  built before 2026-08-19 whose runscript invoked `pixi run` at runtime.
  Rebuild from the current hpc/ files, or work around without a rebuild:

      apptainer exec hitop-cfa.sif bash -c '
        export PATH=/opt/hitop/.pixi/envs/default/bin:$PATH
        python /opt/hitop/notebooks/run_exhaustive_scale.py ...'

  If you want runtime pixi anyway, clear the stale cache path
  (`rm -rf ~/.cache/rattler/cache/uv-cache`) and set
  `PIXI_CACHE_DIR=/tmp/pixi-cache-$USER` -- but the compute nodes'
  lack of network makes this fragile; prefer the rebuild.

- Container sees an EMPTY directory where your data should be
  (`FileNotFoundError`, or `apptainer shell` + `ls` shows nothing at your
  cwd): the path was not bound. Pass it explicitly (`-B /data/MLDSST`) or
  `export APPTAINER_BINDPATH=/data/MLDSST`; the sbatch template already
  binds `$DATA` explicitly.
- `[[: Permission denied` from the runscript: an image built before the
  bash-wrapper fix runs `%runscript` under /bin/sh while the conda
  activation scripts are bash. Harmless for python itself, but rebuild --
  or invoke via `apptainer exec ... bash -c 'source /opt/hitop/activate.sh
  && python ...'` which sidesteps it.
- `Setting LC_* failed` warnings: cosmetic (no locales in the minimal
  image); current images set LC_ALL=C.UTF-8 to silence them.
