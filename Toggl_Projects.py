import pandas as pd
import re
import time
import easygui as e
import os
import sys


##
#Defines global variable arrays
##
def definitions():
    global projectStrings
    global statusStrings
    global resourceStrings
    global ASMX_FA
    global nontraded
    projectStrings = ["ODD", "O&G", "Oil & Gas", "Reg A", "Essential", "Combined", "Interval Fund",
                      "BDC", "DST", "Conservation Easement","Fund", "REIT", "Energy"]
    statusStrings = ["Private", "Public", "NA"]
    resourceStrings = ["Internal", "External", "NA"]
    ASMX_FA = ["ASMX", "FundAmerica"]
    nontraded = ["Non-traded", "Nontraded"]

def directoryStore():
    if not os.path.exists("../Inputs"):
        os.makedirs("../Inputs")
    if not os.path.exists("../Outputs"):
        os.makedirs("../Outputs")

##
#Attempts to data import via pandas, if the file does not exist, then error prompt
#This operation occurs for both 2016 and 2017 data sets
##
def dataLoad():
    try:
        global toggle_preData
        toggle_preData = pd.read_csv("../Inputs/Toggl_projects_2016-01-01_to_2016-12-31.csv")
        global toggle_data
        toggle_data = pd.read_csv("../Inputs/Toggl_projects_2017-01-01_to_2017-12-31.csv")
        toggle_data.columns=['Project type', 'Project', 'Hours', 'Resources', 'Private/public']
        toggle_preData.columns=['Project type', 'Project', 'Hours', 'Resources', 'Private/public']

    except IOError:
        e.msgbox("Could not read file Toggl CSV file. Please re-download that file and put it in the Input folder", "Error")
        sys.exit()

##
#Iterates through the 2017 data, and populates data given from the functions above
##
def dataFormat():
    for x in range(0, len(toggle_data['Project'])):
        toggle_data['Project type'][x] = propertyType(toggle_data['Project'][x],
                                                      toggle_data['Project type'][x])
        toggle_data['Hours'][x] = convertHours(toggle_data['Hours'][x]) + concatenateHours(toggle_data['Project'][x])
        toggle_data['Private/public'][x] = statusType(toggle_data['Project'][x])
        toggle_data['Resources'][x] = resourceType(toggle_data['Project'][x])

def stringBoolean(str, x):
    if str.lower() in x.lower():
        return True
    else:
        return False

##
#Create function to iterate through projectStrings (Project Types),
#and determine if it is a substring of the project title.
#Example: `DST` is a substring of `(final) GK Hy-Vee DST (private or exempt),`
#so then it returns the project type `DST.`
##
def propertyType(str, client):
    for x in range(0, len(projectStrings)):
        if stringBoolean(projectStrings[x], str):
            if stringBoolean(projectStrings[x], "Reg A"):
                for y in range(0, len(ASMX_FA)):
                    if ASMX_FA[y].lower() in client.lower():
                        return (projectStrings[x] + "+ ASMX/FA")
                return (projectStrings[x]+"+ nonASMX/FA")

            for z in range(0, len(nontraded)):
                if stringBoolean(nontraded[z], str):
                    return "Non-traded " + projectStrings[x]
            return projectStrings[x]
    return None
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
#If private in str, then it is private; same for public
#otherwise "NA" is returned
##
def statusType(str):
    for x in range(0, len(statusStrings)):
        if statusStrings[x].lower() in str.lower():
            return statusStrings[x]
    return "NA"

##
#If a project is ODD/Combined, then it does not have a resourceType
#If a project contains (IC), then it is external, otherwise internal
##
def resourceType(str):
    if "ODD".lower() in str.lower() or "Combined".lower() in str.lower():
        return "NA"
    elif ("(IC)").lower() in str.lower():
        return "External"
    else:
        return "Internal"

##
#Given projects in 2017, concatenateHours(Str) looks them up in the 2016 projects
#if there is a match, then the hours are combined
##
def concatenateHours(str):
    for x in range(0, len(toggle_preData['Project'])):
        if str == toggle_preData['Project'][x]:
            return convertHours(toggle_preData['Hours'][x])
    return 0


##
#Tries data export function, retains only `Project` and `Registered time` columns
#and overwrites previous file. If not possible, then error prompt and system exit.
##
def dataExit():
    try:
        toggle_base_url = "../Outputs/Toggl_projects_"
        toggle_timestamp = str(time.strftime("%m-%d-%y"))
        toggle_filetype = ".csv"
        toggle_url = toggle_base_url + toggle_timestamp + toggle_filetype
        toggle_data[['Project', 'Hours', 'Project type', 'Resources', 'Private/public']].to_csv(toggle_url,index=False)
        #os.remove("Toggl_projects_2017-01-01_to_2017-12-31.csv")
        sys.exit()
    except IOError:
        e.msgbox("Could not read file 2016 Toggl CSV file. Please re-download that file and put it in the same directory as this Python script.", "Error")
        sys.exit()

if __name__ == '__main__':
    directoryStore()
    dataLoad()
    definitions()
    dataFormat()
    dataExit()
