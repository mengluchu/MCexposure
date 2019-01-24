
home = raster("C:/Users/Lu000012/Documents/files/trajectory/simu1/1/homewd00.024")
writeRaster(home, "homewd.tif")
commute_median = raster("C:/Users/Lu000012/Documents/files/trajectory/median_wd_comm.tif")
writeRaster(commute_median, "commutewd.tif")

pollu_wnd= raster("C:/Users/Lu000012/Documents/files/trajectory/pol_wnd.tif")
home = (home*5 + pollu_wnd*2)/7
commute_median = (commute_median*5 + pollu_wnd*2)/7


names(commute_median) = "commuter"
names(home) = "homemaker"
writeRaster(home, "homemaker_allweek.tiff")
writeRaster(commute_median, "commuter_allweek.tiff")
