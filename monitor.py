#!/usr/bin/env python

import sqlite3

import os
import time
import glob

# global variables
speriod=(15*60)-1
dbname='/var/www/templog.db'



# store the temperature in the database
def log_temperature(temp):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("INSERT INTO temps values(datetime('now'), (?),(?))", (temp,'1'))

    # commit the changes
    conn.commit()

    conn.close()


# display the contents of the database
def display_data():

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    for row in curs.execute("SELECT * FROM temps"):
        print str(row[0])+"	"+str(row[1])

    conn.close()



# get temerature
# returns None on error, or the temperature as a float
def get_temp(devicefile):

        fileobj = open(devicefile,'r')
        lines = fileobj.readlines()
        fileobj.close()

	tempstr= lines[0]
        tempvalue=float(tempstr)
        #print tempvalue
        return tempvalue



# main function
# This is where the program starts 
def main():

    temperature = get_temp("/tmp/latestAirTemperature.txt")
    if temperature != None:
        print "temperature="+str(temperature)
    else:
        # Sometimes reads fail on the first attempt
        # so we need to retry
        temperature = get_temp("/tmp/latestAirTemperature.txt")
        print "temperature="+str(temperature)

        # Store the temperature in the database
    log_temperature(temperature)

        # display the contents of the database
#        display_data()

#        time.sleep(speriod)


if __name__=="__main__":
    main()
