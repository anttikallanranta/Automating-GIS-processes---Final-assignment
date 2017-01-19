**My code:**
- Asks for simple input from the user
- Allows for a limited customization of the output
- Should be redundant; only taking into account the ID's specified by the user and disregarding 
 invalid input
- Will not create duplicates or process data not specified bu the user


**Parameters and functions:**

def ensure_ID(ID)
  - Ensuring that the user defined ID exists on the testlist (list of all the available ID's) 
  - Takes user defined 7 integer long ID's as input (e.g. 5903912)
  
def ensure_dir(f)
  - Function for making new directories if it doesn't exist
  - Takes user input aggregated with root directory string as input (e.g. /home/geo/Data/grids) 
  
def DandJ(fplist,grid)
  - Imports the .txt files that correspond to the user defined ID's and joins them to the grid layer 
    one by one and saves them as .shp
  - Possible input: fplist = a list of legit filenames specified by the user and refined by the program
                    grid = YKR-grid layer
  
def getPolyCoords(row, geom, coord_type)
  - Returns the coordinates ('x' or 'y') of edges of a Polygon exterior
  - Possible input: row = doesn't get a value in the current setup
                    geom = specified geometry column of the dataframe
                    coord_type = either 'x' or 'y'

def InitYKRFig(grid)
  - Creates an interactive map of the YKR-ID's for the user
  - Possible input: grid = YKR-grid layer
  
def Classifytt(traveltimes, tt)
  - Classifies travel times (10 classes, quantiles)
  - Removes NoData values
  - Returns new traveltimes, does not save anything
  - Possible input: traveltimes = current .shp file (e.g. 2015_5903912.shp)
                    tt = travel mode chosen by the user & travel distance / travel time info (e.g. pt_m_t)
                    
def InitFig(traveltimes, tt, i)
  - Create interactive map of travel times
  - Possible input: traveltimes = same as above
                    tt = same as above
                    i = ID of the .shp file parsed from the filename (e.g. 2015_5903912)
  
def InitStatic(traveltimes, tt, i)
  - Create a static map
  - Possible input: All same as above
  
def VizIDtt(ttlist, maptype)
  - 'Master function' of the visualization functions
  - Download all .shp files from the result_dir and call vizualization functions as per user input
  - Possible input: ttlist = list of travel mode(s) specified by the user. Maximum size = 2 (e.g. ['car', 'pt'])
                    maptype = string variable specified by the user, either '1' (static) or '2' (interactive)
  - Takes only the first item on the ttlist
  
def ttComp(ttlist, maptype, tdt)
  - Travel mode comparison
  - Basically the same as VizIDtt, but specialized in comparing two travel modes either by travel distance
  or travel time
  - Possible input: ttlist = same as above
                    maptype = same as above
                    tdt = string variable specified by the user, either '1' (travel distance) ot '2' (travel time)



**Quick walktrough:**

1.Before running the script: save the marix data into yearly folders inside a directory called 'Matrixes' in /home/geo/Data/
and grid in its own folder in /home/geo/Data/.

2.Answer the questions asked by the program truthfully. However, the script should have the safeguards to disregard 
invalid input.

2.1 You can either save all the output into same folders on each round or create new directories every time
(grids1, grids2...etc / maps1, maps2...etc).

2.2 The program will help you to choose the correct YKR-ID's by generating a map if the user so wishes.

2.3 After creating the .shp files the program prompts the user with visualization options: 
  - static / interactive map 
  - travel mode
The user will be asked to either continue or add another travel type to compare to (substract from) the first one.

3.Visualizations will be saved into user specified output folder.

5.If executed again, the script will ignore all the previous .shp files *if* the user does not give the same ID again.
  However, the final output will not be created if the filepath already exists.
