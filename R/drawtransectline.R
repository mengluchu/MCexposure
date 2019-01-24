#' plot transect lines on the raster map
#'@param ap the raster map where transects are drawn on
#'@param tra_WE West-east line, matrix:rbind(c(xmin,y), c(xmax, y))
#'@param tran_ns North-South line, matrix
#'@param direc which direction to plot, "west-east" or "north-south"
#'@example
#'tra_we= rbind(c(120000,456000), c(145000, 456000))
#'tra_ns= rbind(c(135000,450000), c(135000, 470000))
#'data(homemaker)
#'homemaker = plottransec(homemaker, tra_we, tra_NS = tra_ns)
#'@export

drawtransectline = function(ap, tra_WE=NA, tra_NS=NA){

transects=SpatialLines(list(Lines(list(Line(tra_we)), ID = "west-east"),
                              Lines(list(Line(tra_ns)), ID = "north-south")))
a= rasterVis::levelplot(ap,   par.settings=PuOrTheme(region = rev(brewer.pal(10, 'RdYlGn')[-c(5,6)])), margin=F )+
  #+layer(sp.lines(transects,col=c("red", "purple"),lwd = 2))+
  layer({
    xs <- seq(131432, 133432, by=1000 )
    xs2 = c(xs[1]-400,xs[2]-400,xs[3] )
    grid.rect(x=xs, y=449710,
              width=1000 , height=400,
              gp=gpar(fill=c('transparent', 'black'),2),
              default.units='native')
    grid.text(x=  xs2  , y=450410, c("0", "1", "2 km"),
              gp=gpar(cex=1) ,
              default.units='native')
  })+ layer({
    SpatialPolygonsRescale(layout.north.arrow(),
                           offset = c(140600, 459910),
                           scale = 1000)
  })+
  latticeExtra::layer(sp.lines(transects, pch=c(2,21),lwd = 2, col=brewer.pal(5, 'Set1')[1:2]))
a
}
