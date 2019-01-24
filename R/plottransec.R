#' plot transects
#'@param ap the raster map where transects are drawn on
#'@param tra_WE West-east line, matrix:rbind(c(xmin,y), c(xmax, y))
#'@param tran_ns North-South line, matrix
#'@param direc which direction to plot, "west-east" or "north-south"
#'@example
#'tra_we= rbind(c(120000,456000), c(145000, 456000))
#'tra_ns= rbind(c(135000,450000), c(135000, 470000))
#'WE=plottransec(home, tra_we, tra_NS = tra_ns, "west-east")
#'NS = plottransec(home, tra_we, tra_NS =tra_ns , "north-south")
#'@export

plottransec = function(ap, tra_WE=NA, tra_NS=NA, direc= c("west-east", "north-south"))

{
  transects = SpatialLines(list(Lines(list(Line(tra_WE)), ID = "west-east"),
                                Lines(list(Line(tra_NS)), ID = "north-south")))

  tran1 = extract(ap, transects[direc])
  LE= length(tran1[[1]])
  if (direc == "west-east")
    xaxis1= seq(0, tra_WE[2,1]-tra_WE[1,1], length =LE)/1000
  else
    xaxis1= seq(0, tra_NS[2,2]-tra_NS[1,2],  length =LE)/1000

  trandf = data.frame(trans1 = tran1[[1]], x_axis = xaxis1)
  gg_t=ggplot(trandf, aes(x= xaxis1, y = tran1[[1]])) + geom_line()+
    labs(x = paste( "distrance ", "km"),y =  expression(paste("NO"[2], " ", mu,"g", "/" ,"m"^3)))  + theme_bw()+
    theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),panel.background = element_blank(), axis.line = element_line(colour = "black"))

  gg_t+  theme_classic()

}
