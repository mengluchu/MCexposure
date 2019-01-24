# -*- coding: utf-8 -*-
"""
Created on Tue Dec 05 11:43:38 2017

@author: lu000012
"""
#note: cellvalue returns a vector (value, valid), getCellValue returns a value
import sys
import lue
from pcraster import *
from pcraster.framework import *
import random
import numpy
import csv
import math
import datetime
import os 
import pandas
from gghdc_routing import route_to_pcr_v1
from dateutil.relativedelta import *
import calendar
#import tkMessageBox
filepath = os.path.join("/","data", "expAss_lue")
os.chdir(filepath)
 
 
#############################################    calc               #############
def coord_to_rowcol(xcoord, ycoord, west, north, cellsize):
    """ This one on entire map """

    xCol = (xcoord - west) / cellsize;
    yRow = (north - ycoord) / cellsize

    col_idx  = int(math.floor(xCol))
    row_idx  = int(math.floor(yRow))

    return row_idx, col_idx
 
def create_propertyset(phenomena, property_set):
        omnipresent = lue.constant_size.time.omnipresent
        ps = omnipresent.create_property_set(phenomena, property_set)   # x,y
        return ps
    
def reserve_point_property(propertyset, propertyname, nr_locations,datatype):
        omnipresent = lue.constant_size.time.omnipresent
        space_domain_p = omnipresent.same_shape.create_property(
                propertyset,propertyname, datatype,(2,))
        pointsarray = space_domain_p.reserve(nr_locations)
    
        points_ = numpy.zeros(nr_locations * 2, dtype=datatype)
        points_ = points_.reshape(nr_locations, 2)
        pointsarray[:] = points_
        return pointsarray
     
       
def reserve_raster_property(propertyset, propertyname, nr_locations, window_size_x, window_size_y,datatype):
        # We here add two raster properties, the surrounding and one for a result
    # here we fill in the cut areas
        omnipresent = lue.constant_size.time.omnipresent
        pavement = omnipresent.same_shape.create_property(
                propertyset, propertyname, datatype, (window_size_x, window_size_y))
        values_p = pavement.reserve( nr_locations)
    
        values_p_ = numpy.zeros(( nr_locations *  window_size_x * window_size_y,), dtype=datatype)
        values_p_ = values_p_.reshape( nr_locations,  window_size_x, window_size_y)
        values_p[:] = values_p_
        return values_p
    
    
    
def load_route_LUE(propertyset, nr_locations, homedf, workdf, window_size_x, window_size_y, property_name ):
   
      route_raster =  reserve_raster_property(propertyset, property_name, nr_locations, window_size_x, window_size_y, numpy.float32)
      for i in range(0, nr_locations ):
                         sys.stdout.write("\rGenerating item {0}".format(i))
                         sys.stdout.flush()                          
                         numpy_array= route_to_pcr_v1(homedf.iloc[i,0], homedf.iloc[i,1], workdf.iloc[i,0], workdf.iloc[i,1], server=server_ip)                   
                         #route_raster = numpy2pcr(Boolean, numpy_array, 0.0)
                         
                         route_raster[i] = numpy_array
                         
                
def load_home_work_LUE (propertyset, nr_locations, homedf, workdf, prop_name_home_p, prop_name_home_rc, prop_name_work_p, prop_name_work_rc, nl_west, nl_north,cellsize):
         phome_points = reserve_point_property(propertyset, prop_name_home_p , nr_locations, numpy.float32) 
         phome_rowcol = reserve_point_property(propertyset, prop_name_home_rc , nr_locations,numpy.int32)  
         pwork_points  = reserve_point_property(propertyset, prop_name_work_p, nr_locations,numpy.float32)     
         pwork_rowcol = reserve_point_property(propertyset, prop_name_work_rc, nr_locations,numpy.int32)      

         for i in range(0, nr_locations ):
                         sys.stdout.write("\rGenerating item {0}".format(i))
                         sys.stdout.flush()                         
                         #home
                         xcoord_home = float(homedf.iloc[i,0])
                         ycoord_home = float(homedf.iloc[i,1])
                         row_idx_home, col_idx_home = coord_to_rowcol(xcoord_home, ycoord_home, nl_west, nl_north, cellsize)
                         
                         phome_points[i] = numpy.array([xcoord_home, ycoord_home], dtype=numpy.float32)
                         phome_rowcol[i] = numpy.array([row_idx_home, col_idx_home], dtype=numpy.int32)
                         
                         #work
                         xcoord_work = float(workdf.iloc[i,0])
                         ycoord_work = float(workdf.iloc[i,1])
                         row_idx_work, col_idx_work = coord_to_rowcol(xcoord_work, ycoord_work, nl_west, nl_north, cellsize)
                          
                         pwork_points[i] = numpy.array([xcoord_work, ycoord_work], dtype=numpy.float32)
                         pwork_rowcol[i] = numpy.array([row_idx_work, col_idx_work], dtype=numpy.int32)
 

def get_nrrow_nrcol_west_south_north_east(hdf5file, phenomena_name):
        dataset = lue.open_dataset( hdf5file, "r")   
        phenomenon = dataset.phenomena[ phenomena_name] 
        pset = dataset.phenomena[phenomena_name].property_sets["area"]

        nr_rows = pset["band_1"].space_discretization.values[:][0][0]
        nr_cols = pset["band_1"].space_discretization.values[:][0][1]

        nl_west = pset.domain.space.items[:][0][0]
        nl_south = pset.domain.space.items[:][0][1]
        nl_north = pset.domain.space.items[:][0][3]
        nl_east = pset.domain.space.items[:][0][2]
        return nr_rows, nr_cols, nl_west, nl_south, nl_north, nl_east
   
def coor2map(window_size_x, window_size_y,  loc_row,loc_col,data_type):
                     array0= numpy.zeros((window_size_x * window_size_y,), dtype=data_type)
                     clone_array = array0.reshape(window_size_x, window_size_y)
                     clone_array[loc_row, loc_col]=1
                     startcell = numpy2pcr(Boolean,  clone_array, 0.0)
                     return startcell

def exposure_road(routearray, pol_map, velocity_second_m, celllength):
                     
                        route_raster = numpy2pcr(Boolean, routearray, 0.0)
                        nr_cells, valid = cellvalue(mapmaximum(uniqueid(route_raster)),1,1)
                        exposure,valid = cellvalue(maptotal(ifthen(route_raster, pol_map)),1,1)  
                    #exposure, valid = cellvalue(mapmaximum(areatotal(pol,route_raster)),1,1)
                    #exposure, valid = cellvalue(areatotal(pol,route_raster), long(home_loc_row),long(home_loc_col))
                 
                        exposure = exposure / nr_cells 
                    # what about diagonal directions? :-) Can't we get the length of the path from OSML++?
                        commute_time = celllength *velocity_second_m* nr_cells  #celllength(), 20m
                        return exposure, commute_time             
                    
            
def exposure_point(point_raster, pol_map):
                        pointexposure,valid = cellvalue(mapmaximum(ifthen(point_raster, pol_map)),1,1)
                        return pointexposure
                    
def move2startcell(point_raster, cellexposure):
                        cellexp = scalar(cellexposure)
                        exposure_Map1  = ifthen(point_raster, cellexp)
                        return exposure_Map1
                                
server_ip = "172.17.0.2"  

 
class MyFirstModel(DynamicModel,MonteCarloModel):
#class MyFirstModel(DynamicModel):
  
  def __init__(self):
    DynamicModel.__init__(self)
    MonteCarloModel.__init__(self)
    setclone(os.path.join('NO2_Input','re_road_length_5000.map'))
    
  def premcloop(self):
    #self.windowbuffer = 20 #20m buffer is the same as no buffer  
    self.windowbuffer = 60 #20m buffer  
    self.startDate = datetime.datetime(2017, 1, 2, 0, 0)
    self.annual = True
    self.road_length_5000_file = os.path.join('NO2_Input', 're_heavy_traf_load_50.map') 
    self.heavy_traf_load_50 =  readmap(os.path.join('NO2_Input','re_heavy_traf_load_50.map'))
    self.major_road_length_25 = readmap( os.path.join('NO2_Input', 're_major_road_length_25.map'))
    self.road_length_1000 = readmap( os.path.join('NO2_Input', 're_road_length_1000.map'))
    self.road_length_5000 = readmap( os.path.join('NO2_Input', 're_road_length_5000.map'))
    #self.csv_input = "ishomes.csv"
    self.hdf5file = "temp20.h5"
    self.phenomena_name = "re_road_length_5000"
    
    self.lue_phenomena = "exposure"
     
    self.lue_ps_points = "frontdoor"
    self.lue_ps_area = "routes"
    self.lue_p_area_route = "osm_routes"     
    self.lue_p_points_home = "home_locations"
    self.lue_p_points_home_rowcol = "home_rowcol"
    self.lue_p_points_work = "work_locations"
    self.lue_p_points_work_rowcol = "work_rowcol"
    
    self.home_csv = "woon.csv" 
    self.homedf = pandas.read_csv(self.home_csv)
    self.work_csv = "working_snrh.csv" 
    self.workdf = pandas.read_csv(self.work_csv)  #for randomly sample working locations
    self.home_raster = "woon20m.map"
    
    cmd = "col2map -S -s, --clone {0} -x 1 -y 2 -v 3 {1} {2} ".format(self.road_length_5000_file, self.home_csv,  self.home_raster)
    subprocess.check_call(cmd, shell=True)
    
  
    ## travel duration through a cell (s, seconds)
    # velocity on the road (km/h)
    self.celllength =  getCellValue(celllength(),1,1)
    self.velocity= 16.0
    self.velocityMPerSecond=(self.velocity*1000.0)/(60.0*60.0)
    self.velocitySecondPerM=1.0/self.velocityMPerSecond
    self.durationPerCellOnRoad=self.velocitySecondPerM*self.celllength 
 
    #self.ids = uniqueid(boolean(self.home_raster))
    #self.nr_locations, Valid = cellvalue(mapmaximum(self.ids),1,1)
  #  self.nr_locations = int(self.nr_locations)
#    if self.homedf.shape[0]!=self.workdf.shape[0]:
#        tkMessageBox.showerror('this model', 'the number of working locations is not equal to home locations')

    self.nr_locations = self.homedf.shape[0]
    print self.nr_locations, self.workdf.shape[0]
    #self.nr_locations =1 
    
  def initial (self):
    self.startmap =scalar(0)
    self.startmap_home = scalar(0)
    
    self.lue_name =   os.path.join("LUE", "exposure_{0}.lue".format(str(self.currentSampleNumber()) )) 
    self.currentDate = self.startDate 
    #pcraster.setrandomseed(self.currentSampleNumber()*1000) 
    
    #random.seed(self.currentSampleNumber()*1000)
    self.workdf =  self.workdf.sample(frac=1, replace=True,random_state = self.currentSampleNumber()*1000 ) #randomly sample working locations
     
    self.work_realisation = os.path.join(str(self.currentSampleNumber()),"work_realisation.csv") 
    self.workloc = os.path.join(str(self.currentSampleNumber()),"work_loc.map") # for testing
    self.workdf.to_csv(self.work_realisation, header = False) #save each realisation
    cmd = "col2map -S -s, --clone {0} -x 2 -y 3 -v 1 {1} {2} ".format(self.road_length_5000_file, self.work_realisation, self.workloc)
    subprocess.check_call(cmd, shell=True)
    #get extent form hdf file
    
    nr_rows, nr_cols, nl_west, nl_south, nl_north, nl_east = get_nrrow_nrcol_west_south_north_east(self.hdf5file, self.phenomena_name)
    cellsize = (nl_east - nl_west) / nr_cols
    
    self.window_size_x = int(nr_rows)
    self.window_size_y = int(nr_cols)
    
  
    print "input dataset:", nl_west, nl_south, nl_north, nl_east, nr_rows, nr_cols, cellsize, self.window_size_x, self.window_size_y

# Here create the new dataset if LUE does not exists.
    if os.path.isfile(self.lue_name) == False:
        
        
        dataset = lue.create_dataset(self.lue_name)
        # add phenomenon
        phenomenon_exposure = dataset.add_phenomenon(self.lue_phenomena)
        #add propertyset
        ps_points = create_propertyset(phenomenon_exposure, self.lue_ps_points)
        ps_areas = create_propertyset(phenomenon_exposure, self.lue_ps_area)    
        
        #load properties       
        
        # ids for the properties are necessary for now                    
        ids_front = ps_points.reserve(self.nr_locations)
        ids_area = ps_areas.reserve(self.nr_locations)
        # assign a unique id
        ids_front[:] =  range(0, self.nr_locations  )
        ids_area[:] =  range(0, self.nr_locations  )
        
        load_route_LUE(ps_areas, self.nr_locations, self.homedf, self.workdf, self.window_size_x,self.window_size_y,self.lue_p_area_route)                
        #load work and home locations to LUE            
        load_home_work_LUE(ps_points, self.nr_locations, self.homedf, self.workdf,  self.lue_p_points_home, 
                           self.lue_p_points_home_rowcol, self.lue_p_points_work, self.lue_p_points_work_rowcol, nl_west, nl_north,cellsize)    
    
        lue.assert_is_valid(dataset)
 
#open LUE for use
    dataset = lue.open_dataset(self.lue_name, "w")
    phenomenon = dataset.phenomena[self.lue_phenomena]
    self.route_set = phenomenon.property_sets[self.lue_ps_area] 
    self.pslocations =  phenomenon.property_sets[self.lue_ps_points]      
 
    self.timestep=1
    #self.exposure_Map = scalar(1)
    
   # self.array0= numpy.zeros((self.window_size_x * self.window_size_y,), dtype=numpy.float32)
   # self.clone_array_home = self.array0.reshape(self.window_size_x,self.window_size_y)
   # for i in range(1, self.nr_locations):
   #                 home_loc_row = int(self.pslocations[self.lue_p_points_home_rowcol].values[i][:][0])
   #                 home_loc_col = int(self.pslocations[self.lue_p_points_home_rowcol].values[i][:][1])
   #                # w_loc_row = self.pslocations[self.lue_p_points_work_rowcol].values[i][:][0]
   #                # w_loc_col = self.pslocations[self.lue_p_points_work_rowcol].values[i][:][1]
   #                # home_loc_row1 = self.pslocations[self.lue_p_points_home].values[i][:][0])
   #                # home_loc_col2 =  self.pslocations[self.lue_p_points_home].values[i][:][1])
   #                # print home_loc_row, home_loc_col, home_loc_row1, home_loc_col2, w_loc_col,w_loc_row
   #                 self.clone_array_home[ home_loc_row, home_loc_col ]=1
   # self.startcell_home = numpy2pcr(Boolean,  self.clone_array_home, 0.0) # for homemakers
    self.test_dest = scalar(0)
  def dynamic(self):       
        #v = numpy.array(v, dtype = "bool")
    self.exposure_Map = scalar(0)
    insideProportion = 0.7
    weekday = self.currentDate.weekday()
    hour = self.currentDate.hour
    hour2 = hour +1 # original monthly data has a name column
       # average = pcraster.windowaverage(res,self.window)     
      
    if self.currentDate.weekday() < 5:
            self.dayType = "wkday"
    else:
            self.dayType = "wkend"
            
    #get air pollution coefficients        
    if self.annual != True:   # monthly     
        filename  = "NO2_Input/NO2coeff-m4-"+self.currentDate.strftime("%b").lower()+"-"+self.dayType+".csv" 
        self.coefficients = numpy.genfromtxt(os.path.join(filename), delimiter=",")
           
        pol = self.coefficients[hour2][1] +\
        self.coefficients[hour2][2] *  self.heavy_traf_load_50 +\
        self.coefficients[hour2][3] *  self.major_road_length_25 +\
        self.coefficients[hour2][4] *  self.road_length_1000 +\
        self.coefficients[hour2][5] *  self.road_length_5000
    
    else:
        filename  = "NO2_Input/yearcoef_weekday"+".csv" 
        self.coefficients = numpy.genfromtxt(os.path.join(filename), delimiter=",")
        pol = self.coefficients[hour][1] +\
        self.coefficients[hour][2] *  self.heavy_traf_load_50 +\
        self.coefficients[hour][3] *  self.major_road_length_25 +\
        self.coefficients[hour][4] *  self.road_length_1000 +\
        self.coefficients[hour][5] *  self.road_length_5000 
    # IF we want to use a buffer for at home, first calculate the buffer on the predictors (preprocessing)
    # and then create a polBuffered map or so here
          
    #calculate average
    pol_average = pcraster.windowaverage(pol,self.windowbuffer)  
    print hour
    #self.report(pol_average, "polave")
   # self.report(pol, "pol")
   
   #start modeling 
    if self.dayType == "wkday":
        if hour == 8:
                for i in range(1, self.nr_locations-1):
                   # self.array0= numpy.zeros((self.window_size_x * self.window_size_y,), dtype=numpy.float32)
                    #self.clone_array = self.array0.reshape(self.window_size_x,self.window_size_y)
                    home_loc_row =  self.pslocations[self.lue_p_points_home_rowcol].values[i][:][0] 
                    home_loc_col =  self.pslocations[self.lue_p_points_home_rowcol].values[i][:][1]
                    #print home_loc_row, home_loc_col
                    #home location:
                    startcell = coor2map(self.window_size_x, self.window_size_y,  home_loc_row, home_loc_col, numpy.int32 )
                    #home exposure
                    exp_home = exposure_point(startcell, pol_average )
                    
                    #route exposure and time
                    route_array = self.route_set[self.lue_p_area_route].values[i]
                    #routeraster = numpy2pcr(Boolean, route_array, 0.0)
                    exp_route, commute_time = exposure_road(route_array, pol,self.velocitySecondPerM, self.celllength)
                    
                    #exposure at commuting time
                     
                    cellexp =  exp_route * commute_time + exp_home* (60*60 -commute_time) *insideProportion # arrving work at 1
                    #print cellexp
                    #self.report(startcell,"home"+str(i)) 
                    
                    # why this does not work!
                    #self.exposure_Map = ifthenelse(startcell,scalar(cellexp),self.exposure_Map)
                
                    #self.report(routeraster,"route"+str(i)) 
                    self.exposure_Map1 = move2startcell(startcell, cellexp)
                    #self.report(scalar(cellexp),"cellexp"+str(i))  
                    if i == 1:
                            self.exposure_Map = self.exposure_Map1                         
                    else: 
                           self.exposure_Map = cover(self.exposure_Map  , self.exposure_Map1)   
                                       
                self.report(self.exposure_Map,"at9")     
                  
        elif (hour > 8) & (hour < 17): 
            for i in range(1, self.nr_locations-1 ):
                home_loc_row = self.pslocations[self.lue_p_points_home_rowcol].values[i][:][0]
                home_loc_col = self.pslocations[self.lue_p_points_home_rowcol].values[i][:][1]
                work_loc_row = self.pslocations[self.lue_p_points_work_rowcol].values[i][:][0]
                work_loc_col = self.pslocations[self.lue_p_points_work_rowcol].values[i][:][1]
                
                startcell = coor2map(self.window_size_x, self.window_size_y,  home_loc_row, home_loc_col,numpy.int32  )
                destination = coor2map(self.window_size_x, self.window_size_y,  work_loc_row, work_loc_col,numpy.int32  )
                #print home_loc_row, home_loc_col, work_loc_row, work_loc_col
                
                # work exposure
                
                exp_atwork = exposure_point(destination, pol_average ) # cellvalue at work
                cellexp =  exp_atwork *60.0 *60.0  *insideProportion                
                self.exposure_Map1 = move2startcell(startcell, cellexp)
                    #self.report(scalar(cellexp),"cellexp"+str(i))  
                if i == 1:
                            self.exposure_Map = self.exposure_Map1                         
                else: 
                           self.exposure_Map = cover(self.exposure_Map  , self.exposure_Map1) 
                
                #self.exposure_Map = ifthenelse(startcell,scalar(cellexp),self.exposure_Map)
                #self.report(destination,"work"+str(i)) 
                #self.exposure_Map1 = move2startcell(startcell, cellexp)
                
                #testing
                #self.test_dest = scalar(destination)+self.test_dest
                
                
                #if i == 1:
                #    self.exposure_Map = ifthen(startcell, cellexp)
                #if i == 1:
                #        self.exposure_Map = self.exposure_Map1
                         
               # else: 
                #        self.exposure_Map = cover(self.exposure_Map  , self.exposure_Map1)        
            
            self.report(self.exposure_Map,"atwork")    
            #self.report(self.test_dest, "testr" )
            #self.report(startcell, "testhome")   
            
        elif hour == 17:           
                for i in range(1,self.nr_locations-1):
                    self.array0= numpy.zeros((self.window_size_x * self.window_size_y,), dtype=numpy.float32)
                    self.clone_array = self.array0.reshape(self.window_size_x,self.window_size_y)
 
                # maybe do not recalculate destination again as a PCRaster map as it is the same
                # as at 9am above? 
                    home_loc_row = self.pslocations[self.lue_p_points_home_rowcol].values[i][:][0]
                    home_loc_col =self.pslocations[self.lue_p_points_home_rowcol].values[i][:][1]
                     
                    #home location:
                    startcell = coor2map(self.window_size_x, self.window_size_y,  home_loc_row, home_loc_col,numpy.int32  )
                    #home exposure
                    exp_home = exposure_point(startcell, pol_average )
                    
                    #route exposure and time
                    route_array = self.route_set[self.lue_p_area_route].values[i]
                    exp_route, commute_time = exposure_road(route_array, pol,self.velocitySecondPerM, self.celllength)
                    
                    #exposure at commuting time
                    cellexp =  exp_route * commute_time + exp_home* (60*60 -commute_time) *insideProportion # arrving work at 1
                    #self.exposure_Map = ifthenelse(startcell,scalar(cellexp),self.exposure_Map)
                    self.exposure_Map1 = move2startcell(startcell, cellexp)
                    #self.report(scalar(cellexp),"cellexp"+str(i))  
                    if i == 1:
                            self.exposure_Map = self.exposure_Map1                         
                    else: 
                           self.exposure_Map = cover(self.exposure_Map  , self.exposure_Map1) 
                           
                    #self.exposure_Map1 = move2startcell(startcell, cellexp)
                  #  if i == 1:
                  #          self.exposure_Map = self.exposure_Map1                         
                    #else: 
                     #      self.exposure_Map = cover(self.exposure_Map  , self.exposure_Map1)   
                                       
                self.report(self.exposure_Map,"at18")     
            
                
             
        else:  
            
                #exposure = ifthen(self.startcell_home, pol_average)  
                exposure = ifthen(boolean(self.home_raster), pol_average)  
                #exposure = ifthen(boolean(self.home_raster), pol)
               
                self.exposure_Map = exposure *60 *60 *insideProportion
      # print hour2
                self.report(self.exposure_Map, "athome")
      #  self.currentDate += datetime.timedelta(hours=1)
       
    elif self.dayType == "wkend":
                exposure = ifthen(boolean(self.home_raster), pol_average)
                 
                self.exposure_Map = exposure*60 *60 *insideProportion
 #   if self.currentDate.hour == 0:
     #         self.currentDate += relativedelta(months=1)  #jump to next month
     #         self.currentDate = self.currentDate.replace(day=2)
     #         if self.currentDate.weekday() > 5:
    #               self.currentDate +=datetime.timedelta(days = 7 - self.currentDate.weekday()) #only for weekdays
    self.startmap += self.exposure_Map
    
    #for homemaker
    exposurehome = ifthen(boolean(self.home_raster), pol_average)
    self.exposure_Map_home = exposurehome *60 *60 *insideProportion
    self.startmap_home += self.exposure_Map_home

    print self.currentDate.strftime("%d-%m-%Y %H:%M") 

    if self.timestep == nrOfTimeSteps:
        
       self.startmap = self.startmap/nrOfTimeSteps/3600
       self.report(self.startmap," comm_day")
       self.startmap_home = self.startmap_home/nrOfTimeSteps/3600
       self.report(self.startmap_home,"home_day")
     
    self.timestep+=1
    self.currentDate += datetime.timedelta(hours=1)
    
#####
  def postmcloop(self):
    names=['a_comm'+str(nrOfSamples)]    
    #print celllength()
    sampleNumbers=self.sampleNumbers()
    timeSteps=[24]
    #print timeSteps
 #   mcaveragevariance(names,sampleNumbers,timeSteps)
 #    percentiles=[0.025,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.975]
    percentiles=[ 0.25, 0.5, 0.75 ] 
    mcpercentiles(names,percentiles,sampleNumbers,timeSteps)
 
s1 = datetime.datetime.now() 
nrOfTimeSteps =24*1

nrOfSamples = 30
myModel = MyFirstModel()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
mcModel = MonteCarloFramework(dynamicModel,nrOfSamples)
#mcModel.setForkSamples(True,2)
mcModel.run()

time1 =  datetime.datetime.now() - s1
print time1
