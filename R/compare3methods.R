#' Compare Extract location values from raster results and plot the scatterplot
#' @param rasterlist list of rasters for comparision
#' @param location used \code{\link[raster]{extract}} function, could be e.g. a dataframe with XY to extract locations for comparison.
#' @example homemaker = raster("data/homemaker_allweek.tif"); rl = list(homemaker,commuter,AP_5m); location = read.csv("data/woon.csv", header = F); location = location[,-3]; names(location) = c("X","Y"); commuter = raster("data/commuter_allweek.tif");AP_5m = raster("data/AP_map_5m_Utrecht.tif");compare3methods(rl)
#'devtools::use_package("raster")
require("ggplot2")
require("lattice")
require("GGally")
require(reshape2)
require(raster)


compare3methods = function(rasterlist,location, varnames = c("Homemaker","Commuter", "Static"))
{

dfach= data.frame(lapply(rasterlist, extract, location))
names(dfach) = varnames

my_fn <- function(data, mapping, ...){
  p <- ggplot(data = data, mapping = mapping) +
    geom_point() +
  #  geom_smooth(method=loess, fill="red", color="red", ...) +
    geom_smooth(method=lm, fill="blue", color="blue", ...)
  p
}
ggpairs( dfach,lower = list(continuous = my_fn))
#ggsave(device="png", filename = "comparison.png")
#ggplot(df2, aes(x = variable, y = value))+geom_point()+facet_grid(variable ~ .)
}
