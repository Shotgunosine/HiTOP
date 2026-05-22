from rpy2.robjects import r
r('install.packages(c("lavaan", "semTools", "stringr", "reticulate"), repos = "https://cran.rstudio.com/")')
r('library(lavaan)')
r('library(semTools)')
