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
from dateutil.relativedelta import *
import calendar
from random import randint

#import tkMessageBox
filepath = os.path.join("/","data", "expAss_lue","weekend")
os.chdir(filepath)
 
 
#############################################    calc               #############
def coord_to_rowcol(xcoord, ycoord, west, north, cellsize):
    """ This one on entire map """

    xCol = (xcoord - west) / cellsize;
    yRow = (north - ycoord) / cellsize

    col_idx  = int(math.floor(xCol))
    row_idx  = int(math.floor(yRow))

    return row_idx, col_idx
 
 
class MyFirstModel(DynamicModel,MonteCarloModel):
#class MyFirstModel(DynamicModel):
  
  def __init__(self):
    DynamicModel.__init__(self)
    MonteCarloModel.__init__(self)
    setclone(os.path.join('NO2_Input','re_road_length_5000.map'))
    
  def premcloop(self):
    #self.windowbuffer = 20 #20m buffer is the same as no buffer  
    self.windowbuffer = 60 #20m buffer  
    self.windowbuffer_weekend = 10000 #5000m buffer   
    self.startDate = datetime.datetime(2017, 1, 2, 0, 0)
    self.road_length_5000_file = os.path.join('NO2_Input', 're_heavy_traf_load_50.map') 
    self.heavy_traf_load_50 =  readmap(os.path.join('NO2_Input','re_heavy_traf_load_50.map'))
    self.major_road_length_25 = readmap( os.path.join('NO2_Input', 're_major_road_length_25.map'))
    self.road_length_1000 = readmap( os.path.join('NO2_Input', 're_road_length_1000.map'))
    self.road_length_5000 = readmap( os.path.join('NO2_Input', 're_road_length_5000.map'))
    #self.csv_input = "ishomes.csv"
    self.home_csv = "woon.csv" 
    self.homedf = pandas.read_csv(self.home_csv)
    self.home_raster = "woon20m.map"
    
    cmd = "col2map -S -s, --clone {0} -x 1 -y 2 -v 3 {1} {2} ".format(self.road_length_5000_file, self.home_csv,  self.home_raster)
    subprocess.check_call(cmd, shell=True)

    self.nr_locations = self.homedf.shape[0]
  
   # self.nr_locations =1 
    
  def initial (self):
    self.timestep = 1
    self.startmap_home_weekend = scalar(0)
    self.currentDate = self.startDate 
    #pcraster.setrandomseed(self.currentSampleNumber()*1000) 
    random.seed(self.currentSampleNumber())
    self.hour_random = randint(8, 23) # 9 am : 11pm
    filename  = "NO2_Input/yearcoef_weekend"+".csv" 
    self.coefficients = numpy.genfromtxt(os.path.join(filename), delimiter=",")
    self.pol_weekend = self.coefficients[self.hour_random][1] +\
        self.coefficients[self.hour_random][2] *  self.heavy_traf_load_50 +\
        self.coefficients[self.hour_random][3] *  self.major_road_length_25 +\
        self.coefficients[self.hour_random][4] *  self.road_length_1000 +\
        self.coefficients[self.hour_random][5] *  self.road_length_5000 
    # one hour is outside     
    self.pol_average_weekend_out = pcraster.windowaverage(self.pol_weekend,self.windowbuffer_weekend)  
    
  def dynamic(self):       
        #v = numpy.array(v, dtype = "bool")
    
    insideProportion = 0.7
    weekday = self.currentDate.weekday()
    hour = self.currentDate.hour
 

    filename  = "NO2_Input/yearcoef_weekend"+".csv" 
    self.coefficients = numpy.genfromtxt(os.path.join(filename), delimiter=",")
    self.pol_weekend_home = self.coefficients[hour][1] +\
        self.coefficients[hour][2] *  self.heavy_traf_load_50 +\
        self.coefficients[hour][3] *  self.major_road_length_25 +\
        self.coefficients[hour][4] *  self.road_length_1000 +\
        self.coefficients[hour][5] *  self.road_length_5000 
         
    # IF we want to use a buffer for at home, first calculate the buffer on the predictors (preprocessing)
    # and then create a polBuffered map or so here
          
    #calculate average
    
    self.pol_average_weekend_home = pcraster.windowaverage(self.pol_weekend_home,self.windowbuffer)  
    print hour
 
    #for weekend
    if hour == self.hour_random: 
        self.exposure_weekend_home =   ifthen(boolean(self.home_raster), self.pol_average_weekend_out)
         
    else:    
    #for homemaker
        self.exposure_weekend_home = ifthen(boolean(self.home_raster), self.pol_average_weekend_home)*insideProportion
     
   
    self.startmap_home_weekend += self.exposure_weekend_home
    print self.currentDate.strftime("%d-%m-%Y %H:%M") 

    if self.timestep == nrOfTimeSteps:
            
       self.startmap_home_weekend = self.startmap_home_weekend/nrOfTimeSteps
       self.report(self.startmap_home_weekend,"weeknd")
        
    self.timestep+=1
    self.currentDate += datetime.timedelta(hours=1)
    
#####
  def postmcloop(self):
    names=['weekend']    
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
