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

    apptainer build hitop-cfa.sif hpc/hitop_cfa.def

Option B — anywhere with Docker (note `--platform linux/amd64` when
building on an ARM Mac), then convert:

    docker buildx build --platform linux/amd64 -f hpc/Dockerfile -t hitop-cfa .
    apptainer build hitop-cfa.sif docker-daemon://hitop-cfa:latest

If the cluster disallows local `apptainer build`, check its docs for the
remote builder, or push the Docker image to a registry and
`apptainer build hitop-cfa.sif docker://<registry>/hitop-cfa`.

### Verify the build

Deterministic cross-check against the laptop (same seeds, same worker
count -> same permutation draws):

    apptainer run hitop-cfa.sif run_exhaustive_scale.py insomnia \
        --num-iter 25 --cpus 14 --data-dir /data/finaldata --cfa-dir /tmp/check
    # run the identical command locally (pixi run python ...) and compare
    # the printed results dict; they should match. Small borderline
    # discrepancies would indicate BLAS-level numeric differences --
    # re-check with --num-iter 100 before trusting the image.

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
laptop runs.

Search behavior is identical to the exploratory notebook
(`exhaustive_search_scale`): val_gp-first early abandon, the calibrated
parametric delta screen (alpha = .005; configural never screened),
stepwise-certificate size caps, and per-combination progress persistence
-- a preempted or timed-out task resumes exactly where it stopped when
resubmitted.

## 4. Monitor

    apptainer exec --bind /data/$USER/hitop:/data hitop-cfa.sif \
        pixi run --manifest-path /opt/hitop/pixi.toml \
        python /opt/hitop/notebooks/exploratory_status.py /data/cfa

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
