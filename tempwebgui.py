#!/usr/bin/env python

import sqlite3
import sys
import cgi
import cgitb


# global variables
speriod=(15*60)-1
dbname='/var/www/templog.db'
sensorRoomName="Salon"
#sensors = {
#    1 : 'Salon',
#    2 : 'Chambre'
#}

# print the HTTP header
def printHTTPheader():
    print "Content-type: text/html\n\n"



# print the HTML head section
# arguments are the page title and the table for the chart
def printHTMLHead(title, table):
    print "<head>"
    print "    <title>"
    print title
    print "    </title>"
    
    print_graph_script(table)

    print "</head>"


# get data from the database
# if an interval is passed, 
# return a list of records from the database
def get_data(interval,sensorid):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    id=1
    
    if interval == None:
        curs.execute("SELECT datetime(timestamp,'+1 hour'),temp FROM temps WHERE deviceid="+sensorid)
    else:
        curs.execute("SELECT datetime(timestamp,'+1 hour'),temp FROM temps WHERE deviceid="+sensorid+" AND timestamp>datetime('now','-%s hours')" % interval)
#      curs.execute("SELECT * FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hours') AND timestamp<=datetime('2013-09-19 21:31:02')" % interval)

    rows=curs.fetchall()
    print rows
        
    conn.close()
    return rows


# convert rows from database into a javascript table
def create_table(rows):
    chart_table=""

    for row in rows[:-1]:
        rowstr="['{0}', {1}],\n".format(str(row[0]),str(row[1]))
        chart_table+=rowstr

    row=rows[-1]
    rowstr="['{0}', {1}]\n".format(str(row[0]),str(row[1]))
    chart_table+=rowstr

    return chart_table


# print the javascript to generate the chart
# pass the table generated from the database info
def print_graph_script(table):

    # google chart snippet
    chart_code="""
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Time', 'Temperature'],
%s
        ]);
        var options = {
          title: 'Temperature (\xb0C)'
        };
        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>"""

    print chart_code % (table)




# print the div that contains the graph
def show_graph():
    print "<h3>Temperature Chart</h3>"
    print '<div id="chart_div" style="width: 800px; height: 500px;"></div>'



# connect to the db and show some stats
# argument option is the number of hours
def show_stats(option,sensorid):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    if option is None:
        option = str(24)

    curs.execute("SELECT datetime(timestamp,'+1 hour'),max(temp) FROM temps WHERE deviceid="+sensorid+" AND timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
#    curs.execute("SELECT timestamp,max(temp) FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hour') AND timestamp<=datetime('2013-09-19 21:31:02')" % option)
    rowmax=curs.fetchone()
    rowstrmax="{1} \xb0C at {0}".format(str(rowmax[0]),str(rowmax[1]))

    curs.execute("SELECT datetime(timestamp,'+1 hour'),min(temp) FROM temps WHERE deviceid="+sensorid+" AND timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
 #   curs.execute("SELECT timestamp,min(temp) FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hour') AND timestamp<=datetime('2013-09-19 21:31:02')" % option)
    rowmin=curs.fetchone()
    rowstrmin="{1} \xb0C at {0}".format(str(rowmin[0]),str(rowmin[1]))

    curs.execute("SELECT avg(temp) FROM temps WHERE deviceid="+sensorid+" AND timestamp>datetime('now','-%s hour') AND timestamp<=datetime('now')" % option)
#    curs.execute("SELECT avg(temp) FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-%s hour') AND timestamp<=datetime('2013-09-19 21:31:02')" % option)
    rowavg=curs.fetchone()


    print "<hr>"


    print "<div>Minimum temperature : "+rowstrmin+"</div>"
    print "<div>Maximum temperature : "+rowstrmax+"</div>"
    print "<div>Average temperature : %.3f" % rowavg+" \xb0C</div>"

    print "<hr>"

    print "<h3>In the last hour:</h3>"
    print "<table>"
    print "<tr><td><strong>Date/Time</strong></td><td><strong>Temperature</strong></td></tr>"

    rows=curs.execute("SELECT * FROM temps WHERE deviceid="+sensorid+" AND timestamp>datetime('now','-1 hour') AND timestamp<=datetime('now')")
#    rows=curs.execute("SELECT * FROM temps WHERE timestamp>datetime('2013-09-19 21:30:02','-1 hour') AND timestamp<=datetime('2013-09-19 21:31:02')")
    for row in rows:
        rowstr="<tr><td>{0}&emsp;&emsp;</td><td>{1} \xb0C</td></tr>".format(str(row[0]),str(row[1]))
        print rowstr
    print "</table>"

    print "<hr>"

    conn.close()




def print_time_selector(option,deviceId):

    print """<form action="/cgi-bin/tempwebgui.py" method="POST">
        Show the temperature logs for  
        <select name="timeinterval">"""


    if option is not None:
        
	if option == "1":
            print "<option value=\"1\" selected=\"selected\">the last 1 hours</option>"
        else:
            print "<option value=\"1\">the last 1 hours</option>"

	if option == "2":
            print "<option value=\"2\" selected=\"selected\">the last 2 hours</option>"
        else:
            print "<option value=\"2\">the last 2 hours</option>"

        if option == "6":
            print "<option value=\"6\" selected=\"selected\">the last 6 hours</option>"
        else:
            print "<option value=\"6\">the last 6 hours</option>"

        if option == "12":
            print "<option value=\"12\" selected=\"selected\">the last 12 hours</option>"
        else:
            print "<option value=\"12\">the last 12 hours</option>"

        if option == "24":
            print "<option value=\"24\" selected=\"selected\">the last 24 hours</option>"
        else:
            print "<option value=\"24\">the last 24 hours</option>"

    else:
        print """<option value="6">the last 6 hours</option>
            <option value="12">the last 12 hours</option>
            <option value="24" selected="selected">the last 24 hours</option>"""

    #print """        </select>
     #   Choose a room   
      #  <select name="device">"""


    #if deviceId is not None:

	#if deviceId == "1":
    #        print "<option value=\"1\" selected=\"selected\">Salon</option>"
    #    else:
    #        print "<option value=\"1\">Salon</option>"

	#if deviceId == "2":
     #       print "<option value=\"2\" selected=\"selected\">Chambre</option>"
     #   else:
      #      print "<option value=\"2\">Chambre</option>"

    print """        </select>
        <input type="submit" value="Display">
    </form>"""


# check that the option is valid
# and not an SQL injection
def validate_input(option_str):
    # check that the option string represents a number
    if option_str.isalnum():
        # check that the option is within a specific range
        if int(option_str) > 0 and int(option_str) <= 24:
            return option_str
        else:
            return None
    else: 
        return None


#return the option passed to the script
def get_option():
    form=cgi.FieldStorage()
    if "timeinterval" in form:
        option = form["timeinterval"].value
        return validate_input (option)
    else:
        return None

def get_device():
    form=cgi.FieldStorage()
    if "device" in form:
        deviceId = form["device"].value
        return deviceId
    else:
        return None

def getRoomName(deviceId):
    if int(deviceId) == 1:
        return 'Salon'
    elif int(deviceId) == 2:
        return 'Chambre'

# main function
# This is where the program starts 
def main():

    cgitb.enable()

    # get options that may have been passed to this script
    deviceId=get_device()
    option=get_option()
    
    sensorRoomName=getRoomName(deviceId)

    if option is None:
        option = str(24)
        
    #if deviceId is None:
    #    deviceId = 1   

    # get data from the database
    records=get_data(option,deviceId)

    # print the HTTP header
    printHTTPheader()
    #print "<h1>Device id "+deviceId+" room name : "+str(sensorRoomName)+"</h1>"

    if len(records) != 0:
        # convert the data into a table
        table=create_table(records)
    else:
        print "No data found"
        return

    # start printing the page
    print "<html>"
    # print the head section including the table
    # used by the javascript for the chart
    printHTMLHead("Temperature Logger - "+sensorRoomName, table)

    # print the page body
    print "<body>"
    print "<h3>Temperature Logger - "+sensorRoomName+"</h3>"
    print "<hr>"
    print_time_selector(option,deviceId)
    show_graph()
    show_stats(option,deviceId)
    print "</body>"
    print "</html>"

    sys.stdout.flush()

if __name__=="__main__":
    main()

