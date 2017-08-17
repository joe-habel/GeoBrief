# GeoBrief
A simple program utilizing Google Maps's API to geolocate and plot police CAD data

This program is currently set up based on the only Police CAD system I've been able to deal with.

Currently what is required is that the user's CAD data that they wish to plot be in a csv
file with a delimeter of "|". This is to accomadte normal grammatical descriptions that
use commas. It also asks for there to be no empty rows at the begining of the csv, nor between
the header and the data. The default CAD data header is currently

  INCIDENT # |  DATE AND TIME REPORTED | INCIDENT LOCATION | INCIDENT TYPE
  
  DATE AND TIME formatted as: DD/MM/YYYY HH:MM:SS
  

 
