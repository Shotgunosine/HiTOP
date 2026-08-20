# Reproducible environment for the HiTOP CFA pipeline (linux-64).
# Build FROM THE REPO ROOT:  docker buildx build --platform linux/amd64 \
#     -f hpc/Dockerfile -t hitop-cfa .
# The environment is solved from pixi.lock (linux-64 pins verified against
# the local pipeline: R 4.2.3, rpy2 3.5.1, python 3.11) plus the pinned
# CRAN/GitHub R packages in hpc/install_r_libraries.R.
FROM ghcr.io/prefix-dev/pixi:0.69.0

WORKDIR /opt/hitop

# environment layers first (cache-friendly); src/ is needed at install
# time because hitop-cfa is a pypi editable dependency of the manifest
COPY pixi.toml pixi.lock pyproject.toml ./
COPY src ./src
RUN pixi install --locked

COPY hpc/install_r_libraries.R hpc/install_r_libraries.R
RUN pixi run Rscript hpc/install_r_libraries.R

COPY notebooks/run_exhaustive_scale.py notebooks/exploratory_status.py notebooks/

# bake the activation script so nothing invokes pixi at runtime (runtime
# pixi re-verifies the env and writes caches under $HOME -- fails on NFS
# homes and needs network, neither available on HPC compute nodes)
RUN pixi shell-hook --manifest-path /opt/hitop/pixi.toml > /opt/hitop/activate.sh \
    && printf '#!/bin/bash\nset -e\nsource /opt/hitop/activate.sh\ncd /opt/hitop/notebooks\nexec "$@"\n' \
       > /opt/hitop/entrypoint.sh && chmod +x /opt/hitop/entrypoint.sh

# BLAS must stay single-threaded (permuteMeasEq does the parallelism)
ENV OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    LANG=C.UTF-8 LC_ALL=C.UTF-8

WORKDIR /opt/hitop/notebooks
ENTRYPOINT ["/opt/hitop/entrypoint.sh"]
CMD ["python", "run_exhaustive_scale.py", "--help"]
