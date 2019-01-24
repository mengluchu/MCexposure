#' stratified sampling: divde a raster into grids and ramdomly draw similar amount of data from each grid. The sampled points are moved to the closest target points. In our exposure study, the sampled points are then moved to the nearest home locations.
#' @param ap rastermap
#' @param nrofcells number of grids to be stratified into
#' @param totalpoints total points to be drawn, is an approximation since the points are later moved to the closest target points
#' @param targetpoints the target points location to move to
#' @param  csv if T, store with csv file
#' @param result_name the filename/directory to store the csv file.

#' @return sampled points
#' @example
#'requires library(spatialEco)
#'woon = read.csv("C:/Users/Lu000012/Documents/files/trajectory/woon.csv",header = F)
#' stratified_sampling = function(homemakers, nrofcells=80, totalpoints=1020,targetpoints=woon, result_name="sample_1000.csv")


#' @example proj4string(homemakers) = CRS("+init=EPSG:28992"); stratified_sampling,
#'
stratified_sampling = function(ap, nrofcells=80, totalpoints=1020,targetpoints, csv =T, result_name="sample_1000.csv")
  {
  # fact = 80

stra_grid = aggregate(ap,fact = round(sqrt(ncell(homemaker)/nrofcells)))
stra_grid[!is.na(stra_grid)] = c(1: ncell(stra_grid[!is.na(stra_grid)]))
plot(stra_grid)
#https://www.nceas.ucsb.edu/scicomp/usecases/AssignClosestPointsToPoints
spstra = coordinates(stra_grid)[!is.na(values(stra_grid)),]
spstra=SpatialPoints(spstra)
gridspstra = SpatialPixels(spstra)

sampled = spsample(gridspstra, n = totalpoints, type ="stratified" )
spplot(sampled)
sample_1000=round(data.frame(data.frame(sampled), val = 1), digit =2)

# match to the nearest home location

coordinates(targetpoints) = ~V1 + V2
coordinates(sample_1000) = ~x1 + x2
sample_home= vector(mode = "numeric", length = nrow(sample_1000))
minDistVec= vector(mode = "numeric", length = nrow(sample_1000))

for (i in 1 :nrow(sample_1000))
{
  distVec <- spDistsN1(targetpoints, sample_1000[i,],longlat = TRUE)
  minDistVec[i] <- min(distVec)
  sample_home[i] <- which.min(distVec)
}

sample_1000 = data.frame(data.frame(targetpoints[sample_home,])[,c(1,2)],1)
str(sample_1000)

names(sample_1000) = c("xc", "yc", "id")
return(sample_1000)
names(sample_1000)=NULL
write.csv(sample_1000, result_name,row.names = F )
}

