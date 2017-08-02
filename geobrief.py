from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderQuotaExceeded, GeocoderTimedOut, GeocoderUnavailable
import numpy as np
from math import radians,asin,sin,cos,sqrt
import Tkinter as tk
from tkFileDialog import askopenfilename, askdirectory
import os
from time import sleep
from operator import itemgetter
##################################
'''
Defines the placemark object, as well as defining the functions for updating
certian elements as well as the optional category parameter.
'''
#################################
class Placemark(object):
    def __init__(self,incident,time,datestr,adress,lon,lat,description):
        self.incident = incident
        self.time = time
        self.datestr = datestr
        self.adress = adress
        self.lon = lon
        self.lat = lat
        self.description = description
        self.category = None
    
    def updateAdress(self,addy):
        self.adress = addy
        
    def updateLatLong(self,longitude,latitude):
        self.lon = longitude
        self.lat = latitude
        
    def addCategory(self,category):
        self.category = category

##################################            
'''
This is the main application class. This class contains all the functions that 
are called and manipulated via the GUI.
'''
##################################
class Application(tk.Frame):

    ##################################
    '''
    This function creates the main GUI screen and the main elements on it.
    '''
    ##################################
    def createDefaultWidgets(self):
        self.input_loc = tk.Label(self,text="Input File Location: ")
        self.input_loc.pack()
        self.input_text = tk.Entry(self)
        self.input_text.pack()
        self.input_button = tk.Button(self,text="Select File")
        self.input_button["command"] = self.getInput
        self.input_button.pack()
        self.export_loc = tk.Label(self,text="Export Folder: ")
        self.export_loc.pack()
        self.export_text = tk.Entry(self)
        self.export_text.pack()
        self.export_button = tk.Button(self,text="Select Folder")
        self.export_button.pack()
        self.export_button["command"] = self.getExport
        self.county_label = tk.Label(self,text="County: ")
        self.county_label.pack()
        self.county_text = tk.Entry(self)
        self.county_text.pack()
        self.state_label = tk.Label(self,text="State: ")
        self.state_label.pack()
        self.state_text = tk.Entry(self)
        self.state_text.pack()
        self.Run = tk.Button(self, text="Run")
        self.Run.pack()
        self.Run["command"] = self.run
        self.QUIT = tk.Button(self,text="QUIT")
        self.QUIT.pack()
        self.QUIT["command"] = self.quit
        self.QUIT["fg"] = "red"


    ##################################
    '''
    These are the commands for when the input and export buttons are pressed.
    '''
    ##################################
    
    def getInput(self):
        filename = askopenfilename()
        self.input_text.delete(0,len(self.input_text.get()))
        self.input_text.insert(0,filename)
    
    def getExport(self):
        filepath = askdirectory()
        self.export_text.delete(len(self.export_text.get()))
        self.export_text.insert(0,filepath)
    
    ##################################
    '''
    This is the main run command for the application, from here either the
    program runs without any misplotted points and writes to the KML, or it
    goes through the misplotted points errors.
    '''
    ##################################
    def run(self):
        if self.WE == False:
            self.placemarks = []
        self.errorClear()
        input_loc = self.input_text.get()
        self.export_loc = self.export_text.get()
        self.county = self.county_text.get()
        self.state = self.state_text.get()
        if os.path.isfile(input_loc) is False:
            self.createInputErrorWidgets()
            return
        if os.path.isdir(self.export_loc) is False:
            self.createExportErrorWidgets()
            return
        if self.county is '':
            self.countyError()
            return
        if self.state is '':
            self.stateError()
            return
        
        temp = self.geolocate(input_loc,self.county,self.state)
        if temp is not None:
            self.placemarks.extend(temp)
        if bool(self.placemarks) is False:
            return
        count = 0
        for Placemark in self.placemarks:
            if Placemark.lat is 0:
                count += 1
        logWriter(self.placemarks,self.export_loc)
        self.flags = flaggedPlacemarks(self.placemarks)
        if self.flags[0] == 0:
            KMLwriter(self.placemarks,self.export_loc)
            return
        else:
            self.fixFlagWidgets()    
            return

    ##################################
    '''
    These two functions have yet to be implemented for the ability to query the
    already geolocated data.
    '''
    ##################################

    
    def sortgeolog(self):
        self.export_loc = self.export_text.get()
        self.geologparse()
        self.optionVar = tk.StringVar()
        self.logTop = tk.Toplevel()
        self.logTop.protocol('WM_DELETE_WINDOW', self.overrideX)
        self.logTop.tk.call('wm','iconphoto',self.logTop._w, self.img)
        self.logLab = tk.Label(self.logTop, text="Select what you wish to query for.")
        if self.logPlacemarks[0].category is not None:
            self.queryOption = tk.OptionMenu(self.logTop, self.optionVar, "Date", "Incident Type", "Category")
        else:
            self.queryOption = tk.OptionMenu(self.logTop, self.optionVar , "Date", "Incident Type")
        self.logLab.pack()
        self.queryOption.pack()
        
    def geologparse(self):
        self.logPlacemarks = []
        logdata = np.genfromtxt('%s/geolog.txt'%self.export_loc, dtype=None, comments=None, delimiter= '|')
        if len(logdata[0]) == 6:
            for row in logdata:
                inc = row[0]
                datest = row[1]
                datetime = dateTimeToInt(datest)
                addy = row[2]
                lon = row[3]
                lat = row[4]
                desc = row[5]
                self.logPlacemarks.append(Placemark(inc,datest,datetime,addy,lon,lat,desc))
        if len(logdata[0]) == 7:
            for row in logdata:
                inc = row[0]
                datest = row[1]
                datetime = dateTimeToInt(datest)
                addy = row[2]
                lon = row[3]
                lat = row[4]
                desc = row[5]
                cat = row[6]
                self.logPlacemarks.append(Placemark(inc,datest,datetime,addy,lon,lat,desc))
                self.logPlacemarks[-1].addCategory(cat)
     
    ##################################
    '''
    This function will override the users ability to close any Toplevels.
    '''
    ##################################


    def overrideX(self):
        return
           
    ##################################
    '''
    These functions create the input errors for the four main parameters from
    the main starting point of the GUI.
    '''
    ##################################
    
    def createInputErrorWidgets(self):
        self.input_error = tk.Label(self,text="Invalid Input File")
        self.input_error.pack()
        self.IE = True
        
    def createExportErrorWidgets(self):
        self.export_error = tk.Label(self,text="Invalid Export Path")
        self.export_error.pack()
        self.EE = True
        
    def countyError(self):
        self.county_error = tk.Label(self,text="County cannot be empty")
        self.county_error.pack()
        self.CE = True
        
    def stateError(self):
        self.state_error = tk.Label(self,text="State cannot be empty")
        self.state_error.pack()
        self.SE = True    

    ##################################
    '''
    This automatically detects where the data is in the csv and calls to
    Google's API for geolocation help. It will append to a list of placemarks
    based off of the data from the csv and then detect any api errors and raise
    appropriate warnings for them.
    '''
    ##################################

    def geolocate(self,import_loc,county,state):
        incno = 0
        datetime = 1
        addy = 2
        desc = 3
        self.addcat = False
        skipFirst= False
        if self.WE == False or self.pickup == 0:
            self.Placemarks = []
        data = np.genfromtxt(import_loc, dtype=None, delimiter='|', comments=None)
        for j,row in enumerate(data):
            if row[0] == '':
                data = data[:j]
        for k,element in enumerate(data[0]):
            if element.lower().find("#") >= 0:
                incno = k
                skipFirst = True
            if element.lower().find("type") >= 0:
                desc = k
            if element.lower().find("time") >= 0:
                datetime = k
            if element.lower().find("location") >= 0:
                addy = k
            if element.lower().find("category") >= 0:
                cat = k
                self.addcat = True
        if skipFirst == True:
            data = data[1:]
                
        try:
            if self.WE == False:
                self.geolocator = GoogleV3(timeout=30)
            else:
                self.geolocator = GoogleV3(self.API_key,timeout=30)
            if self.WE == True:
                data = data[self.pickup:]
            for i,rows in enumerate(data):
                if rows[1] == '':
                    continue
                date = rows[datetime]
                if date[0] == ' ':
                    date = date[1:]
                location = self.geolocator.geocode(rows[addy]+ ' ' + county + 'County, ' + state)
                sleep(.25)
                self.geoPlace(i,len(data))
                if location is None:
                    self.Placemarks.append(Placemark(rows[incno],date,rows[datetime],rows[addy],0,0,rows[desc]))
                    if self.addcat == True:
                        self.Placemarks[-1].addCategory(rows[cat])
                else:
                    lon, lat = location.longitude, location.latitude
                    date = dateTimeToInt(date)
                    self.Placemarks.append(Placemark(rows[incno],date,rows[datetime],rows[addy],lon,lat,rows[desc]))
                    if self.addcat == True:
                        self.Placemarks[-1].addCategory(rows[cat])
            return self.Placemarks
        except GeocoderQuotaExceeded:
            self.getNewAPI()
            self.pickup = i
            return                 
        except GeocoderTimedOut:
            self.timeoutError()
            return                
        except GeocoderUnavailable:
            self.unavailableError()
            return
        
        
    ##################################
    '''
    The next two pop-ups will occur on the odd chance that the Google API times
    out or that it isn't available.
    '''
    ##################################

    def timeoutError(self):
        self.timeoutTL = tk.Toplevel()
        self.timeoutTL.protocol('WM_DELETE_WINDOW', self.overrideX)
        self.timeoutTL.tk.call('wm','iconphoto',self.timeoutTL._w, self.img)
        self.timeoutLabel = tk.Label(self.timeoutTL,text="The Google API appears to have timed out. Please quit and restart the program.")
        self.timeoutQuit = tk.Button(self.timeoutTL, text="QUIT", fg="red")
        self.timeoutQuit["command"] = self.quit
        self.timeoutLabel.pack()
        self.timeoutQuit.pack()
        
    def unavailableError(self):
        self.uTL = tk.Toplevel()
        self.uTL.protocol('WM_DELETE_WINDOW', self.overrideX)
        self.uTL.tk.call('wm','iconphoto',self.uTL._w, self.img)
        self.uL = tk.Label(self.uTL, text="The Google API is currently unavailable. Please quit and restart the program. If this message persists, wait before attempting to restart the program.")
        self.uQuit = tk.Button(self.uTL, text="QUIT", fg="red")
        self.uQuit["command"] = self.quit
        self.uL.pack()
        self.uQuit.pack()
        
    ##################################
    '''
    This funciton will display a counter showing how many points have been
    geolocated onto the main screen of the GUI
    '''
    ##################################
  
    def geoPlace(self,current_no,length):
        self.hf = True
        if current_no == 0:
            self.how_far = tk.StringVar()
            self.how_far.set("%i/%i locations geolocated" %((current_no+1),length))
            self.how_far_lab = tk.Label(self,textvariable=self.how_far)
            self.how_far_lab.pack()
        self.how_far.set("%i/%i locations geolocated" %((current_no+1),length))
        self.update()
        self.how_far_lab.update_idletasks()
        if current_no+1 == length:
            self.how_far_lab.destroy()
    
    ##################################
    '''
    These three funtions will deal with the Google's API limit. It will display
    a pop-up allowing the user to enter in a new API key along with a button
    to explain what this error means.    
    '''
    ##################################
    
    
    def getNewAPI(self):
        self.wiki_top = tk.Toplevel()
        self.wiki_top.protocol('WM_DELETE_WINDOW', self.overrideX)
        self.wiki_top.tk.call('wm','iconphoto',self.wiki_top._w, self.img)
        self.wiki_label = tk.Label(self.wiki_top,text="You went over the free 2500 call quota. Please enter a new API Key: ")
        self.wiki_what_this = tk.Button(self.wiki_top,text="What's this")
        self.wiki_what_this["command"] = self.whatThis
        self.wiki_text = tk.Entry(self.wiki_top)
        self.wiki_sub = tk.Button(self.wiki_top,text="Submit")
        self.wiki_sub["command"] = self.wikisub
        self.wiki_label.pack()
        self.wiki_text.pack()
        self.wiki_sub.pack()
        self.wiki_what_this.pack()
        self.WE = True
        
    def wikisub(self):
        self.API_key = self.wiki_text.get()
        self.wiki_top.destroy()
        if self.pickup > 0:
            self.how_far_lab.pack_forget()
        self.run()
                 
    def whatThis(self):
        self.TL = tk.Toplevel()
        self.TL.tk.call('wm','iconphoto',self.TL._w, self.img)
        self.help_text = ''' 
        Google's API only allows for 2500 free calls a day to it's server. 
        If you wish to continue to use this tool, consider attaining a new API key from google.
        If you have a new API key entered into the field, click submit to restart the program. '''
        self.help_label = tk.Label(self.TL, text = self.help_text)
        self.help_label.pack()
        
    ##################################
    '''
    This function will clear any errors from the main screen when the run
    command is executed.    
    '''
    ##################################

        
    def errorClear(self):
        if self.IE == True:
            self.input_error.destroy()
        if self.EE == True:
            self.export_error.destroy()
        if self.CE == True:
            self.county_error.destroy()
        if self.SE == True:
            self.state_error.destroy()
 
    ##################################
    '''
    This pop-up will occur if points have been detected to either be significantly
    different from the rest of the points, or if the Google API couldn't geolocate
    them. The users will be prompted with the amount of bad points and will have 
    the option to fix or ignore these issues. If the user chooses to ignore them,
    points that Google could not geolocate will be mapped to 0,0,0.
    '''
    ##################################
    
        
    def fixFlagWidgets(self):
        self.flag_top = tk.Toplevel()
        self.flag_top.protocol('WM_DELETE_WINDOW', self.overrideX)
        self.flag_top.tk.call('wm','iconphoto',self.flag_top._w, self.img)
        self.broken = tk.StringVar()
        self.broken.set("We've found that %i point(s) are believed to be misplotted. Do you wish to fix them?" %self.flags[0])
        self.fix_flag_label = tk.Label(self.flag_top,textvariable=self.broken)
        self.Yes_button = tk.Button(self.flag_top,text="Yes", fg="green")
        self.Yes_button["command"] = self.yesCommand
        self.No_button = tk.Button(self.flag_top,text="No",fg="red")
        self.No_button["command"] = self.noCommand
        self.fix_flag_label.pack()
        self.Yes_button.pack()
        self.No_button.pack()
        self.update()

    ##################################
    '''
    If the user opts to fix the points, they will be shown the addresses of the 
    points were flagged and for the reasons that they were flagged. The user then
    has the choice to either remove said points or to try to fix the addresses.
    '''
    ##################################

    def yesCommand(self):
        self.flag_top.destroy()
        self.update()
        self.fixTop = tk.Toplevel()
        self.fixTop.protocol('WM_DELETE_WINDOW', self.overrideX)
        self.fixTop.tk.call('wm','iconphoto',self.fixTop._w, self.img)
        self.misplot = tk.StringVar()
        self.mp = ''
        self.np = ''
        self.noplot = tk.StringVar()
        if len(self.flags[1]) > 0:
            for flag in self.flags[1]:
                self.np += flag.adress + "\n"
            self.noplot.set(self.np)
        if len(self.flags[2]) > 0:
            for flag in self.flags[2]:
                self.mp += flag.adress + "\n"
            self.misplot.set(self.mp)
        if self.mp != '':
            self.misplotlab = tk.Label(self.fixTop,textvariable=self.misplot)
            self.misinfolab = tk.Label(self.fixTop,text="The following adresses were believed to be misplotted.")
            self.misinfolab.pack()
            self.misplotlab.pack()
        if self.np != '':
            self.noplotlab = tk.Label(self.fixTop,textvariable=self.noplot)
            self.noinfolab = tk.Label(self.fixTop,text="The following adresses could not be plotted.")
            self.noinfolab.pack()
            self.noplotlab.pack()
        self.update()
        self.fixlabel = tk.Label(self.fixTop,text="What would you like to do to these points?")
        self.deleteButton = tk.Button(self.fixTop, text="Delete", fg="red")
        self.fixButton = tk.Button(self.fixTop, text="Fix")
        self.deleteButton["command"] = self.deletePoints
        self.fixButton["command"] = self.fixPoints
        self.fixlabel.pack()
        self.fixButton.pack()
        self.deleteButton.pack()
        self.update()

    ##################################
    '''
    This function will delete the points if the user specifies delete.    
    '''
    ##################################
     
    def deletePoints(self):
        if self.mp != '':
            for misplot in self.flags[2]:
                self.placemarks.remove(misplot)
        if self.np != '':
            for noplot in self.flags[1]:
                self.placemarks.remove(noplot)
        logWriter(self.placemarks,self.export_loc)
        KMLwriter(self.placemarks,self.export_loc)
        self.fixTop.destroy()
    
    ##################################
    '''
    This function will prompt the user to re-enter a address for the misplotted 
    points. The function will wait for the user to enter each new address before
    prompting for the next one.
    '''
    ##################################

    
    def fixPoints(self):
        self.fixTop.destroy()
        self.entryTop = tk.Toplevel()
        self.entryTop.protocol('WM_DELETE_WINDOW', self.overrideX)
        self.entryTop.tk.call('wm','iconphoto',self.entryTop._w, self.img)
        self.addytofix = tk.StringVar()
        self.fixedaddy = tk.Entry(self.entryTop)
        if self.mp != 0:
            self.mplab = tk.Label(self.entryTop, text="The following appear to be misplotted.")
            for flag in self.flags[2]:
                self.move_on = False
                self.addytofix.set(flag.adress)
                self.addyLab = tk.Label(self.entryTop,textvariable=self.addytofix)
                self.subButton = tk.Button(self.entryTop, text="Update")
                self.subButton["command"] = lambda: self.updateEntry(flag)
                self.addyLab.pack()
                self.fixedaddy.pack()
                self.subButton.pack()
                self.update() 
                self.wait_window(self.addyLab)
        if self.np != 0:
            self.mplab = tk.Label(self.entryTop, text="The following could not be plotted.")
            for flag in self.flags[1]:
                self.move_on = False
                self.addytofix.set(flag.adress)
                self.addyLab = tk.Label(self.entryTop,textvariable=self.addytofix)
                self.subButton = tk.Button(self.entryTop, text="Update")
                self.subButton["command"] = lambda: self.updateEntry(flag)
                self.addyLab.pack()
                self.fixedaddy.pack()
                self.subButton.pack()
                self.update() 
                self.wait_window(self.addyLab)
        self.entryTop.destroy()
        logWriter(self.placemarks,self.export_loc)
        KMLwriter(self.placemarks,self.export_loc)

    ##################################
    '''
    This function will update the lat/long information of the points, and check
    if the address could be located. If the address can't be located, the user
    will recieve a pop-up giving them the option to enter lat/long information,
    or they have the option to delete this point. This function will also
    check for the Google API error exceptions and handle them with the 
    same pop-ups as in the geoplace function.    
    '''
    ##################################

        
    def updateEntry(self,placemark):
        placemark.updateAdress(self.fixedaddy.get())
        try:
            location = self.geolocator.geocode(placemark.adress +' ' + self.county + 'County, ' + self.state)
            if location is not None:
                placemark.updateLatLong(location.longitude,location.latitude)
            if location is None:
                self.againMiss = tk.Toplevel()
                self.againMiss.protocol('WM_DELETE_WINDOW', self.overrideX)
                self.againMiss.tk.call('wm','iconphoto',self.againMiss._w, self.img)
                self.badaddy = tk.StringVar()
                self.badaddy.set(placemark.adress)
                self.badaddyLab = tk.Label(self.againMiss, textvariable=self.badaddy)
                self.misslab = tk.Label(self.againMiss, text="This adress again could not be located. If you wish to plot it please enter a latitude and longitude, or else you can delete this point.")
                self.latLab = tk.Label(self.againMiss, text="Latitude")
                self.fixlatEnt = tk.Entry(self.againMiss)
                self.lonLab = tk.Label(self.againMiss, text="Longitude")
                self.fixlonEnt = tk.Entry(self.againMiss)
                self.latlonSub = tk.Button(self.againMiss, text="Submit")
                self.latlonSub["command"] = lambda: self.latlonfix(placemark)
                self.latlonDel = tk.Button(self.againMiss, text="Delete", fg="red")
                self.latlonDel["command"] = lambda: self.latlondel(placemark)
                self.badaddyLab.pack()
                self.misslab.pack()
                self.latLab.pack()
                self.fixlatEnt.pack()
                self.lonLab.pack()
                self.fixlonEnt.pack()
                self.latlonSub.pack()
                self.latlonDel.pack()
                self.update()
                self.wait_window(self.badaddyLab)
        except GeocoderQuotaExceeded:
            self.getNewAPI()
            self.wait_window(self.wiki_top)
            self.geolocator = GoogleV3(self.API_key,timeout=30)
            location = self.geolocator.geocode(placemark.adress +' ' + self.county + 'County, ' + self.state)
            if location is not None:
                placemark.updateLatLong(location.longitude,location.latitude)
            if location is None:
                self.againMiss = tk.Toplevel()
                self.againMiss.protocol('WM_DELETE_WINDOW', self.overrideX)
                self.againMiss.tk.call('wm','iconphoto',self.againMiss._w, self.img)
                self.badaddy = tk.StringVar()
                self.badaddy.set(placemark.adress)
                self.badaddyLab = tk.Label(self.againMiss, textvariable=self.badaddy)
                self.misslab = tk.Label(self.againMiss, text="This adress again could not be located. If you wish to plot it please enter a latitude and longitude, or else you can delete this point.")
                self.latLab = tk.Label(self.againMiss, text="Latitude")
                self.fixlatEnt = tk.Entry(self.againMiss)
                self.lonLab = tk.Label(self.againMiss, text="Longitude")
                self.fixlonEnt = tk.Entry(self.againMiss)
                self.latlonSub = tk.Button(self.againMiss, text="Submit")
                self.latlonSub["command"] = lambda: self.latlonfix(placemark)
                self.latlonDel = tk.Button(self.againMiss, text="Delete", fg="red")
                self.latlonDel["command"] = lambda: self.latlondel(placemark)
                self.badaddyLAb.pack()
                self.misslab.pack()
                self.latLab.pack()
                self.fixlatEnt.pack()
                self.lonLab.pack()
                self.fixlonEnt.pack()
                self.latlonSub.pack()
                self.latlonDel.pack()
                self.update()
                self.wait_window(self.badaddyLab)
        except GeocoderTimedOut:
            self.timeoutError()
        except GeocoderUnavailable:
            self.unavailableError()
        self.fixedaddy.delete(0,len(self.fixedaddy.get()))
        self.addyLab.destroy()
        self.fixedaddy.pack_forget()
        self.subButton.destroy()
        self.move_on = True
        self.update()        

    ##################################
    '''
    These two functions will either update the lat/long or it will delete it.    
    '''
    ##################################


    def latlonfix(self,placemark):
        placemark.updateLatLong(float(self.fixlonEnt.get()),float(self.fixlatEnt.get()))
        self.againMiss.destroy()
        
    def latlondel(self,placemark):
        self.placemarks.remove(placemark)
        self.againMiss.destroy()

    ##################################
    '''
    This is the command if the user didn't want to fix any points.    
    '''
    ##################################
    
    def noCommand(self):
        self.flag_top.destroy()
        self.update()
        logWriter(self.placemarks)
        KMLwriter(self.placemarks, self.export_loc)
            
    ##################################
    '''
    This init handles the error occurances, and the image file for the GUI    
    '''
    ##################################


    def __init__(self,master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createDefaultWidgets()
        self.SE= False
        self.CE = False
        self.EE = False
        self.IE = False
        self.WE = False
        self.cont = False
        self.hf = False  
        self.pickup = 0
        self.img = tk.Image("photo", file="Earth.gif")


##################################
'''
This function will parse the CAD formatted date and time string and convert it 
into a tuple of ints.    
'''
##################################

def dateTimeToInt(date):
    first_back_loc = date.find('/')
    month = int(date[:first_back_loc])
    second_back_loc = date.find('/',first_back_loc+1)
    day = int(date[first_back_loc+1:second_back_loc])
    space_loc = date.find(' ',second_back_loc+1)
    year = int(date[second_back_loc+1:space_loc])
    first_colon_loc = date.find(':')
    hour = int(date[space_loc+1:first_colon_loc])
    second_colon_loc = date.find(':',first_colon_loc+1)
    minute = int(date[first_colon_loc+1:second_colon_loc])
    if second_colon_loc > 0:
        sec = int(date[second_colon_loc+1:])
        return (year,month,day,hour,minute,sec)
    else:
        return (year,month,day,hour,minute)

##################################
'''
This function will take in a list of placemarks and return a list of these
placemarks sorted temportally, to then be written to the kml file.
'''
##################################

def dateTimeSort(placemark_list):
    time_list = []
    places = []
    for placemark in placemark_list:
        if len(placemark.time) == 6:
            dTime = placemark.time[0]*10000000000+placemark.time[1]*100000000+placemark.time[2]*1000000+placemark.time[3]*10000+placemark.time[4]*100+placemark.time[5]
        else:
            dTime = placemark.time[0]*100000000+placemark.time[1]*1000000+placemark.time[2]*10000+placemark.time[3]*100+placemark.time[4]
        time_list.append((placemark,dTime))
    sorted_tups = sorted(time_list, key=itemgetter(1))
    for tup in sorted_tups:
        places.append(tup[0])
    return places
        
##################################
'''
This function will write a list of placemarks to a user specified export path.
The defualt name for this kml file is MapFile, this parameter will be changed
as the query functionality is added.
'''
##################################


def KMLwriter(Placemark_list,export_loc,file_name="MapFile"):
    Placemark_list = dateTimeSort(Placemark_list)
    KML = open('%s/%s.kml'%(export_loc,file_name),'w')
    KML.write('<?xml version="1.0" encoding="UTF-8"?> \n<kml xmlns="http://www.opengis.net/kml/2.2"> \n<Document>\n')
    for placemark in Placemark_list:
        KML.write('<Placemark> \n')
        KML.write('<name>%s</name>'%placemark.description)
        KML.write('<description><![CDATA[<header> <h3>%s</h3> </header> <p>%s<br>%s</p>]]></description>\n'%(placemark.adress,placemark.datestr,placemark.incident))
        KML.write('<Point> \n')
        KML.write('<coordinates>%f,%f,0</coordinates>\n'%(placemark.lon,placemark.lat))
        KML.write('</Point> \n')
        KML.write('</Placemark> \n')
    KML.write('</Document> \n</kml>')
    KML.close()

    
##################################
'''
This function writes the geolocated placemarks to a new csv file including lat/
long data, to allow the user to re-parse without having to call to Google's API.
This will be accessed more when querieng is used.
'''
##################################

def logWriter(placemark_list,export_loc):
    with open('%s/geolog.txt' %export_loc, 'w') as log:
        for placemark in placemark_list:
            if placemark.category is None:
                log.write('%s|%s|%s|%f|%f|%s \n'%(placemark.incident, placemark.datestr, placemark.adress, float(placemark.lon), float(placemark.lat), placemark.description))
            else:
                log.write('%s|%s|%s|%f|%f|%s|%s \n'%(placemark.incident, placemark.datestr, placemark.adress, float(placemark.lon), float(placemark.lat), placemark.description, placemark.category))

##################################
'''
This calculates the distance between two points given their lat/long.
'''
##################################
                
def haversine(lat1, lon1, lat2, lon2):
  R = 6372.8 
  dLat = radians(lat2 - lat1)
  dLon = radians(lon2 - lon1)
  lat1 = radians(lat1)
  lat2 = radians(lat2)

  a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
  return R*2*asin(sqrt(a))

##################################
'''
This will run a MADS significance test to flag outliers in a data set.
'''
##################################

def MADS(dists,thresh=3.5):
    med = np.median(dists)
    abs_dev = np.abs(dists - med)
    left_mad = np.median(abs_dev[dists <= med])
    right_mad = np.median(abs_dev[dists >= med])
    dist_mad = left_mad*np.ones(len(dists))
    dist_mad[dists > med] = right_mad
    mod_z_score = 0.6745 * abs_dev/dist_mad
    mod_z_score[dists == med] = 0
    return mod_z_score > thresh

##################################
'''
This function will take in a list of placemarks and check if the have a
geolocation and also use the above two functions to check for any outliers.
It returns the amount of flagged placemarks, as well as a list of each type.
'''
##################################

def flaggedPlacemarks(placemark_list):
    placemark_list_copy = list(placemark_list)
    nonetypeplacemarks = []
    misplottedplacemarks = []
    for placemark in placemark_list_copy:
        if int(round(placemark.lon)) is 0:
            nonetypeplacemarks.append(placemark)
            #placemark_list_copy.remove(placemark)
    dists = np.zeros(len(placemark_list_copy))
    for i,placemark in enumerate(placemark_list_copy):
        dists[i] += haversine(placemark.lat,placemark.lon,0,0)
    for i,element in enumerate(MADS(dists)):
        if element is True:
            misplottedplacemarks.append(placemark_list[i])
            #placemark_list_copy.remove(placemark_list[i])
            
    return len(nonetypeplacemarks) + len(misplottedplacemarks), nonetypeplacemarks, misplottedplacemarks
    
##################################
'''
This main is used to root the tkinter GUI, title it, re-size it, and alter the
icon.
'''
##################################    
    
root = tk.Tk()
app = Application(master=root)
root.wm_title("GeoBrief")
root.tk.call('wm','iconphoto',root._w, app.img)
root.geometry('{}x{}'.format(400, 400))
app.mainloop()
root.destroy()
