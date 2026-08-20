#!/bin/bash
# Run the overnight notebooks headlessly, in order, stopping if one fails.
#
# Usage (from anywhere):
#   caffeinate -i ./notebooks/run_overnight.sh            # default chain
#   caffeinate -i ./notebooks/run_overnight.sh NB_2_cfa_as_reg.ipynb  # custom
#
# caffeinate -i keeps macOS awake while the runner works. Each notebook is
# executed with jupyter nbconvert --inplace, so on success its outputs are
# saved into the notebook itself, exactly as if run interactively. On a
# FAILURE the notebook FILE is left unchanged (nbconvert aborts before
# writing) -- but the pipeline's own incremental artifacts
# (orig_cfa_res_in_progress.csv, *_in_progress.pkl, run_errors.log, the
# stage logs) persist regardless, so completed work is never lost and
# progress can be watched mid-run:
#   tail -f notebooks/log/overnight_runner.log
#   ls -l data/cfa/
#
# Default chain is the two permutation-heavy CFA notebooks only. The
# downstream notebooks (NB_3_ICC etc.) are deliberately NOT chained:
# review the exhaustive results / review-note cells first.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p log
RUNLOG=log/overnight_runner.log

NOTEBOOKS=("$@")
if [ ${#NOTEBOOKS[@]} -eq 0 ]; then
    NOTEBOOKS=(NB_2_cfa_as_reg.ipynb NB_2_cfa_exploratory.ipynb)
fi

echo "[$(date '+%F %T')] overnight runner starting: ${NOTEBOOKS[*]}" | tee -a "$RUNLOG"
for nb in "${NOTEBOOKS[@]}"; do
    echo "[$(date '+%F %T')] executing $nb ..." | tee -a "$RUNLOG"
    if pixi run jupyter nbconvert --to notebook --execute --inplace \
        --ExecutePreprocessor.timeout=-1 "$nb" >> "$RUNLOG" 2>&1; then
        echo "[$(date '+%F %T')] finished $nb OK" | tee -a "$RUNLOG"
    else
        echo "[$(date '+%F %T')] $nb FAILED -- stopping the chain." \
             "See $RUNLOG for the traceback; completed scales are preserved" \
             "in the in-progress artifacts under ../data/cfa/." | tee -a "$RUNLOG"
        exit 1
    fi
done
echo "[$(date '+%F %T')] overnight runner finished: all notebooks OK" | tee -a "$RUNLOG"
