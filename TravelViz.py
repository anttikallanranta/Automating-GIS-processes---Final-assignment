# -*- coding: utf-8 -*-
"""
Lets user make simple static or interactive visualizations of the 
Helsinki Region Travel Time Matrix data (2013 / 2015).

Matrix data must be stored into /home/geo/data/matrixes/
prior to running the script!

Antti Kallanranta 21.12.2016
"""
import os
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pysal as ps
from pathlib import Path
import glob
from bokeh.plotting import figure, save, show, output_file
from bokeh.models import ColumnDataSource, LogColorMapper, HoverTool, Patches
from bokeh.palettes import RdYlBu11 as palette
from bokeh.tile_providers import STAMEN_TONER
import fiona
from fiona.crs import from_epsg

#Assign all the folder connections
ykrfp = r'/home/geo/Data/MetropAccess_YKR_grid/MetropAccess_YKR_grid_EurefFIN.shp'
rootdir = r'/home/geo/Data/Matrixes'
result_dir = r'/home/geo/Data/' + input('Specify a directory name for joined layers: ')
viz_dir = r'/home/geo/Data/' + input('Specify a directory name for visualizations: ')

#Make a list of all YKR grid IDs
grid = gpd.read_file(ykrfp)
IDseries = grid.ix[1:, 'YKR_ID']
IDs = IDseries.tolist()
        
#Ensuring that the user defined ID exists on the testlist (list of all the available ID's)
def ensure_ID(ID):
    if ID in testlist:
        print('Processing file ' + str(ID))
        return True
    elif not ID in testlist:
        print('ID not on list.')
        return False

#Create lists of all the ID's & their paths in the 2013/2015 directories       
testlist = [] 
pathlist = []       
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        p = str(subdir) + '/' + str(file)
        pathlist.append(p)
        ID=file[-11:-4]
        testlist.append(ID)

#Function for making new directories if it doesn't exist
def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f) 

#Create a result directory if it doesn't already exist
ensure_dir(result_dir) 
#Create a new directory for visualizations if it doesn't already exist
ensure_dir(viz_dir)        
     
#Import the .txt files that correspond to the user defined ID's 
#Join them to the grid one by one and save as .shp
def DandJ(fplist,grid):
    for i in fplist:
        ttdata = pd.read_csv(i, sep=';')
        join = grid.merge(ttdata, left_on = 'YKR_ID', right_on = 'from_id')  
        outfp = result_dir + '/' + i[-41:-37] + '_' + i[-11:-4] + '.shp'
        #Check if the filepath already exists
        if not os.path.isfile(outfp)==True:        
            join.to_file(outfp)
        else:
            return False
    print('Join complete.')

#Get polygon coordinates
def getPolyCoords(row, geom, coord_type):
    """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior"""
    # Parse the exterior of the coordinate
    exterior = row[geom].exterior
    if coord_type == 'x':
        # Get the x coordinates of the exterior
        return list( exterior.coords.xy[0] )
    elif coord_type == 'y':
        # Get the y coordinates of the exterior
        return list( exterior.coords.xy[1])

#Interactive map of the YKR-ID's for the user
def InitYKRFig(grid):
    ykrs = grid.ix[1:, 'YKR_ID']
    YKR_ID = ykrs.tolist()
    grid['geometry'] = grid['geometry'].to_crs(from_epsg(3857))
    grid.crs = from_epsg(3857)
    
    grid['x'] = grid.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
    grid['y'] = grid.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)
    g_df = grid.drop('geometry', axis=1).copy()
    gsource = ColumnDataSource(g_df)
    
    fig = figure(title='YKR IDs',
                 plot_height=800,plot_width=800)
    fig.axis.visible = False
    fig.add_tile(STAMEN_TONER)
    my_hover = HoverTool()
    my_hover.tooltips = [('YKR-ID: ', '@YKR_ID')]
    fig.add_tools(my_hover)
    color_mapper = LogColorMapper(palette=palette)
    fig.patches('x', 'y', source=gsource,
         fill_color={'field': 'YKR_ID', 'transform': color_mapper},
         fill_alpha=0.8, line_color="black", line_width=0.05)
    
    outfp=viz_dir + '/' + 'YKR_IDs_interactive.html'
    if not os.path.isfile(outfp)==True:
        save(fig, outfp)    
        
#User specified list of ID's
while True:
    user = input('''Would you like to have a map of the possible YKR-IDs? 
    Yes [1]
    No [2]
    ''')
    if user == '1':
        InitYKRFig(grid)
        print('Map has been created into ' + viz_dir)
    break
userlist=[]
while True:
    data=input('Specify ID: ')
    if data=='c':
        break
    if len(data)==7:    
        userlist.append(data)
    print('Specify another / to continue, type [c]')
    
#Testing if the user ID's exist in the list of all available ID's
#Appending a list of their filepaths for file import
fplist = []
ip = 0        
for ID in userlist:
    ensure_ID(ID)
    ip += 1
    print('Progress: ' + str(ip) + '/' + str(len(userlist)))
    if ensure_ID(ID)==True:
        #Checking if user defined ID's are a part of existing filenames
        #and appending the final list 
        fp = [el for el in pathlist if el and (ID in el)]
        for i in fp:            
            fplist.append(i)
 
#.txt's to .shp's      
DandJ(fplist,grid)

##PT 2
###Visualizing
        
#Classify travel times
def Classifytt(traveltimes, tt):        
    # Remove NoData values
    traveltimes = traveltimes[(traveltimes.T !=-1).any()]
    #Create classifier
    n_classes=10
    classifier=ps.Quantiles.make(k=n_classes)
    #Classify travel times into a new column
    traveltimes[tt + '_class']=traveltimes[[tt]].apply(classifier)
    return traveltimes
    
#Create interactive map of travel times
def InitFig(traveltimes, tt, i):
    traveltimes = Classifytt(traveltimes, tt)
    traveltimes['geometry'] = traveltimes['geometry'].to_crs(from_epsg(3857))
    traveltimes.crs = from_epsg(3857)
    
    traveltimes['x'] = traveltimes.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
    traveltimes['y'] = traveltimes.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)
    tt_df = traveltimes.drop('geometry', axis=1).copy()
    ttsource = ColumnDataSource(tt_df)

    fig = figure(title='Travel times to ' + i,
                 plot_height=800,plot_width=800)
    fig.axis.visible = False
    fig.add_tile(STAMEN_TONER)
    my_hover = HoverTool()
    my_hover.tooltips = [('Travel time to ' + str(i) + ': ', '@%s'%(tt))]
    fig.add_tools(my_hover)
    color_mapper = LogColorMapper(palette=palette)
    fig.patches('x', 'y', source=ttsource,
         fill_color={'field': tt +'_class', 'transform': color_mapper},
         fill_alpha=0.8, line_color="black", line_width=0.05)
    
    outfp=viz_dir + '/' + i + '_' + tt + '_interactive.html'
    if not os.path.isfile(outfp)==True:
        save(fig, outfp)
        
#Create static map
def InitStatic(traveltimes, tt, i):
    traveltimes = traveltimes[(traveltimes.T !=-1).any()]
    my_map = traveltimes.plot(column=tt, linewidth=0.03, cmap="Reds", scheme="quantiles", k=9, alpha=0.9)
    plt.tight_layout()
    if len(ttlist)>=2:
        outfp=viz_dir + '/' + i + '_' + tt + '_static.png'    
        if not os.path.isfile(outfp)==True:
            plt.savefig(outfp, dpi=300)
    elif len(ttlist)==1:
        outfp=viz_dir + '/' + i + '_' + tt + '_static.png'    
        if not os.path.isfile(outfp)==True:
            plt.savefig(outfp, dpi=300)
    
#Download all .shp files from the result_dir
#Call vizualization functions as per user input
def VizIDtt(ttlist, maptype):
    filepaths = glob.glob(result_dir + '/' + '*.shp')    
    fps = []
    #Iterating over the filepaths in case there's some files from previous runs
    for f in filepaths:
        i = str(f[-11:-4])
        if i in userlist:
            fps.append(f)
    #Iterate over the valid filepaths, update the 'tt' variable and call visualization functions
    for f in fps:
        i = str(f[-16:-4])
        traveltimes = gpd.read_file(f)
        if ttlist[0]=='car' or ttlist[0]=='pt':        
            tt = ttlist[0] + '_m_t'
            if maptype=='1':
               InitStatic(traveltimes, tt, i) 
            elif maptype=='2':
               InitFig(traveltimes, tt, i)                
        elif ttlist[0]=='walk':
            tt = ttlist[0] + '_t'
            if maptype=='1':
                InitStatic(traveltimes, tt, i)
            elif maptype=='2':
               InitFig(traveltimes, tt, i) 
 
#Travel mode comparison
def ttComp(ttlist, maptype, tdt):
    filepaths = glob.glob(result_dir + '/' + '*.shp')
    for f in filepaths:
        i = str(f[-16:-4])
        traveltimes = gpd.read_file(f)
        #Assign correct variable names
        if tdt == '2':
            if ttlist[0] == 'walk':
                t1 = ttlist[0] + '_t'
            else:
                t1 = ttlist[0] + '_m_t'
            if ttlist[1] == 'walk':
                t2 = ttlist[1] + '_t'
            else:
                t2 = ttlist[1] + '_m_t'
        elif tdt == '1':
            if ttlist[0] == 'walk':
                t1 = ttlist[0] + '_d'
            else:
                t1 = ttlist[0] + '_m_d'
            if ttlist[1] == 'walk':
                t2 = ttlist[1] + '_d'
            else:
                t2 = ttlist[1] + '_m_d'
        #Iterate over the rows to create a new t1-t2 column    
        for index, row in traveltimes.iterrows():
            traveltimes[ttlist[0] + '_vs_' + ttlist[1]] = traveltimes[t1]-traveltimes[t2]  
            tt = ttlist[0] + '_vs_' + ttlist[1]
        #Save the .shp
        outfp = f +'_' + t1 + '_vs_' + t2 + '.shp'
        traveltimes.to_file(outfp)
        #Make maps
        if maptype =='1':
            InitStatic(traveltimes, tt, i)
        elif maptype == '2':
            InitFig(traveltimes, tt, i)

#User input
ttoptions = ['car', 'pt', 'walk']
mapoptions = ['static [1]', 'interactive [2]']
ttlist = []
tdt = ''
maptype = input('Specify map type ' + str(mapoptions) + ': ')

while True: 
    if len(ttlist) == 0:
        tt = input('Specify travel mode ' + str(ttoptions) + ': ')   
    if tt in ttoptions:    
        ttlist.append(tt)
    else:
        print('Invalid input')
    if len(ttlist) == 1:
        tt = input('''Specify another travel mode for comparison 
/ to continue, type [c]\n''' + str(ttoptions) + ': ')
        if tt == 'c':
            break
        if tt in ttoptions:            
            ttlist.append(tt)
        else:
            print('Invalid input')
        if len(ttlist) == 2:
            tdt = input('''Would you like to compare travel distance [1] 
            or travel time [2]? 
                ''')
            break
    
#Calling functions based on the list length
if len(ttlist)==1:
    VizIDtt(ttlist, maptype) 
elif len(ttlist)>1:
    ttComp(ttlist, maptype, tdt)

        