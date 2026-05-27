from rpy2.robjects import r
r('install.packages(c("lavaan", "stringr", "reticulate"), repos = "https://cran.rstudio.com/")')
r("""
        library(devtools)
        install_github("shotgunosine/semTools/semTools@db294f2")
        """
    )
r('library(lavaan)')
r('library(semTools)')