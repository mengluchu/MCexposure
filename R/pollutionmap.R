#' calculate air pollution map, only used in the project (not going to publish)
#' @param dir the directory folder of NO2_input
#' @export

APmap = function(dir = "C:/Users/Lu000012/Documents/files/trajectory/NO2_Input/")
{
  yearcoef = read.csv(paste(dir, "yearcoef.csv", sep= ""), header = T)

#names(yearcoef) = c("ID", "intercept", "heavytraf_load_50", "major_road_len_25","road_len_1000", "road_len_5000","p_v","R2")
#yearcoef$ID = c(1:nrow(yearcoef))
#yearcoef$ID = NULL
#rownames(yearcoef) = NULL
#write.csv(yearcoef,"C:/Users/Lu000012/Documents/files/trajectory/NO2_Input/yearcoef.csv",row.names = F)
#library(raster)
yearcoef = yearcoef[,c(-1,  -7,-8)] # from ivan's file, column 1,7,8 are ID, R2 and p-value, so removed
yearcoefmean =  apply(yearcoef,2, mean)

v1_hea_traf_load50= raster (paste(dir, "heavy_traf_load50_Utreht.tif", sep= ""))
v2_major_road_len25= raster (paste(dir, "major_road_len25_Utreht.tif", sep= ""))
v3_road_len1000= raster(paste(dir, "road_len1000_Utreht.tif", sep= ""))
v4_road_len5000= raster(paste(dir, "roadlen5000_Utreht.tif", sep= ""))

APmap = with(data.frame(t(yearcoefmean)),
     intercept + heavytraf_load_50*v1_hea_traf_load50 + major_road_len_25*v2_major_road_len25 +
         road_len_1000*v3_road_len1000 + road_len_5000*v4_road_len5000)
APmap
}
#Ap_map_5m_utrecht = APmap()
#writeRaster(Ap_map_5m_utrecht, filename = "AP_map_5m_Utrecht.tif")
