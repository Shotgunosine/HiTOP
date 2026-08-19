# R packages not available from conda, pinned to the versions validated by
# the local pipeline (see HANDOFF_measeq_fix.md: semTools 0.5-8 fork with
# the defend_parallel fix, commit db294f2; lavaan 0.7-2).
options(repos = c(CRAN = "https://cran.rstudio.com/"))
remotes::install_version("lavaan", version = "0.7-2", upgrade = "never")
install.packages(c("stringr", "reticulate"))
remotes::install_github("shotgunosine/semTools/semTools@db294f2", upgrade = "never")
stopifnot(packageVersion("lavaan") == "0.7.2",
          packageVersion("semTools") == "0.5.8.903")
library(lavaan)
library(semTools)
cat("R package install OK\n")
