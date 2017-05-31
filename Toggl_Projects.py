
# coding: utf-8

# In[22]:


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import time
import easygui as e
get_ipython().magic(u'matplotlib inline')

#Data import via pandas
try:
    toggle_preData = pd.read_csv("Toggl_projects_2016-01-01_to_2016-12-31.csv")
except IOError:
    e.msgbox("Could not read file 2016 Toggl CSV file. Please re-download that file and put it in the same directory as this Python script.", "Error")
    exit()
    
try:
    toggle_data = pd.read_csv("Toggl_projects_2017-01-01_to_2017-12-31.csv")
except IOError:
    e.msgbox("Could not read file 2016 Toggl CSV file. Please re-download that file and put it in the same directory as this Python script.", "Error")
    exit()

toggle_data.columns=['Project type', 'Project', 'Hours', 'Resources', 'Private/public']
toggle_preData.columns=['Project type', 'Project', 'Hours', 'Resources', 'Private/public']
#Define the finite amount of Project Types
projectStrings = ["ODD", "O&G", "Oil & Gas", "Reg A", "Essential", "Combined", "Interval Fund", 
                  "BDC", "DST", "Conservation Easement","Fund", "REIT", "Energy"]
statusStrings = ["Private", "Public", "NA"]
resourceStrings = ["Internal", "External", "NA"]
##
#Create function to iterate through projectStrings (Project Types), 
#and determine if it is a substring of the project title.
#Example: `DST` is a substring of `(final) GK Hy-Vee DST (private or exempt),`
#so then it returns the project type `DST.`
##
def propertyType(str, client):
    for x in range(0, len(projectStrings)):
        if projectStrings[x].lower() in str.lower():
            if projectStrings[x] == "Reg A":
                if "ASMX".lower() in client.lower() or "FundAmerica".lower() in client.lower():
                    return (projectStrings[x]+"+ ASMX/FA")
                else:
                    return (projectStrings[x]+"+ nonASMX/FA")
            if "nontraded" in str.lower() or "non-traded" in str.lower():
                return "Non-traded " + projectStrings[x]
            return projectStrings[x]
    return "NA"
##
#Create function to strip numbers for the HH:MM:SS format
#and convert this into decimal format by hours
##
def convertHours(str):
    hour = float()
    str_list = str.split(':')
    float_list = [float(x) for x in str_list]
    for x in range(0, len(float_list)):
        hour += float_list[x]/(60**float(x))
    return hour

##
#
#
##
def statusType(str):
    for x in range(0, len(statusStrings)):
        if statusStrings[x].lower() in str.lower():
            return statusStrings[x]
    return "NA"

##
#
#
##
def resourceType(str):
    if "ODD".lower() in str.lower() or "Combined".lower() in str.lower():
        return "NA"
    elif ("(IC)").lower() in str.lower():
        return "External"
    else:
        return "Internal"

##
#
#
##
def concatenateHours(str):
    for x in range(0, len(toggle_preData['Project'])):
        if str == toggle_preData['Project'][x]:
            return convertHours(toggle_preData['Hours'][x])
    return 0
##
#
#
##
for x in range(0, len(toggle_data['Project'])):
    toggle_data['Project type'][x] = propertyType(toggle_data['Project'][x], 
                                                  toggle_data['Project type'][x])
    toggle_data['Hours'][x] = convertHours(toggle_data['Hours'][x]) + concatenateHours(toggle_data['Project'][x])
    toggle_data['Private/public'][x] = statusType(toggle_data['Project'][x])
    toggle_data['Resources'][x] = resourceType(toggle_data['Project'][x])

toggle_data     
##
#Data export function, retains only `Project` and `Registered time` columns 
#and overwrites previous file
##
toggle_base_url = "Toggl_projects_"
toggle_timestamp = str(time.strftime("%m-%d-%y"))
toggle_filetype = ".csv"
toggle_url = toggle_base_url + toggle_timestamp + toggle_filetype
toggle_data[['Project', 'Hours', 'Project type', 'Resources', 'Private/public']].to_csv(toggle_url,index=False)

