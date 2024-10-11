# Name: Lisette Ruano
# Class: CS 341, Fall 2024
# Overview: Project 1 - CTA Database App

import sqlite3
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter


##################################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    dbCursor.execute("Select count(*) From Stations;")
    total_stations = dbCursor.fetchone();
    dbCursor.execute('select count(*) from Stops')
    total_stops = dbCursor.fetchone();
    dbCursor.execute('select count(*) from Ridership')
    total_entries = dbCursor.fetchone();
    dbCursor.execute('SELECT strftime("%Y-%m-%d", min(Ride_Date)) from Ridership')
    min_date = dbCursor.fetchone();
    dbCursor.execute('SELECT strftime("%Y-%m-%d", max(Ride_Date)) from Ridership')
    max_date = dbCursor.fetchone();
    dbCursor.execute('SELECT sum(Num_Riders) from Ridership')
    max_riders = dbCursor.fetchone();

    print("  # of stations:", f"{total_stations[0]:,}")
    print("  # of stops:", f"{total_stops[0]:,}")
    print("  # of ride entries:", f"{total_entries[0]:,}")
    print('  date range:', min_date[0], "-", max_date[0])
    print("  Total ridership:", f"{max_riders[0]:,}")
    print()



# Command 1
#
# findStation
#
# Executes a single SQL query to find and output all 
# matching or similar station names and their station IDs 
# to the input provided by the user
def findStation(dbConn):
    print()
    dbCursor = dbConn.cursor()

    station_input = input("Enter partial station name (wildcards _ and %): ")

    query = """select Station_ID, Station_Name 
            from Stations where Station_Name 
            like ? order by Station_Name asc"""
    dbCursor.execute(query, (station_input,))
    stationResults = dbCursor.fetchall();

    if stationResults:
        for station in stationResults:
            print(f"{station[0]} : {station[1]}")
    else:
        print("**No stations found...")
    print()



# Command 2
#
# findPercentages
#
# Executes two SQl queries in order to find 
# the total weekday, saturday, and sunday/holiday ridership
# and their percentages for a specific station
def findPercentages(dbConn):
    print()
    dbCursor = dbConn.cursor()
    nameInput = input("Enter the name of the station you would like to analyze: ")

    query = """select Type_of_Day, sum(Num_Riders) as Total_Riders 
            from Stations join Ridership 
            on Ridership.Station_ID=Stations.Station_ID 
            where Station_Name = ? group by Type_of_Day 
            order by Total_Riders desc"""
    dbCursor.execute(query, (nameInput,))
    dayPercentages = dbCursor.fetchall();

    query = """select sum(Num_Riders) as Total_Riders 
            from Stations join Ridership 
            on Ridership.Station_ID=Stations.Station_ID 
            where Station_Name = ?"""
    dbCursor.execute(query, (nameInput,))
    totalResult = dbCursor.fetchone();

    totalNum = totalResult[0]
   
    if dayPercentages:
        for day in dayPercentages:
            if day[0] == 'W':
                weekdayResult = day[1]
                weekdayPercentage = (weekdayResult/totalNum) * 100
            elif day[0] == 'A':
                saturdayResult = day[1]
                satPercentage = (saturdayResult/totalNum) * 100
            else:
                sundayResult = day[1]
                sunPercentage = (sundayResult/totalNum) * 100
        print("Percentage of ridership for the", nameInput, "station:")
        print("  Weekday ridership:", f"{weekdayResult:,}", f"({weekdayPercentage:.2f}%)")
        print("  Saturday ridership:", f"{saturdayResult:,}", f"({satPercentage:.2f}%)")
        print("  Sunday/holiday ridership:", f"{sundayResult:,}", f"({sunPercentage:.2f}%)")
        print("  Total ridership:", f"{totalNum:,}")
    else:
        print("**No data found...")
    print()



# Command 3
#
# weekdayRidership
#
# Executes two SQl queries in order to find and output every station's 
# total ridership and their percentage for the weekdays
def weekdayRidership(dbConn):
    wChar = 'W'
    dbCursor = dbConn.cursor()
    print("Ridership on Weekdays for Each Station")

    query = """select sum(Num_Riders) from Ridership where Type_of_Day = ?"""
    dbCursor.execute(query,(wChar,))
    row = dbCursor.fetchone();

    totalWeekdayNum = row[0]

    query = """select Station_Name, sum(Num_Riders) as Total_Riders 
            from Stations join Ridership 
            on Ridership.Station_ID=Stations.Station_ID 
            where Type_of_Day = ? group by Station_Name 
            order by Total_Riders desc"""
    dbCursor.execute(query,(wChar,))
    allStations = dbCursor.fetchall();

    for station in allStations:
        weekdayPercentage = (station[1]/totalWeekdayNum) * 100
        print(station[0], ":", f"{station[1]:,}", f"({weekdayPercentage:.2f}%)" )
    print()



# Command 4
#
# lineAndDirection
#
# Executes a variety of SQL queries in order to find and output
# every stop on a specific line color and going a specific direction
# based on the user's inputs
def lineAndDirection(dbConn):
    print()
    dbCursor = dbConn.cursor()
    lineColor = input("Enter a line color (e.g. Red or Yellow): ")

    query = """select Line_ID from Lines where Color like ?"""
    dbCursor.execute(query,(lineColor,))
    color = dbCursor.fetchone();

    if not color:
        print("**No such line...")
        print()
        return

    lineDirection = input("Enter a direction (N/S/W/E): ")

    query = """select Stop_Name, ADA from Lines join Stops 
            on Stops.Stop_ID=StopDetails.Stop_ID 
            join StopDetails on StopDetails.Line_ID=Lines.Line_ID 
            where Color like ? and Direction like ? 
            order by Stop_Name asc"""    
    dbCursor.execute(query,(lineColor,lineDirection,))
    stopNames = dbCursor.fetchall();
    
    if not stopNames:
        print("**That line does not run in the direction chosen...")
        print()
        return

    for stop in stopNames:
        if stop[1] == 1:
            print(stop[0], ":", "direction =", lineDirection.upper(), "(handicap accessible)")
        else:
            print(stop[0], ":", "direction =", lineDirection.upper(), "(not handicap accessible)")
    print()



# Command 5
#
# colorPercentages
#
# Executes a variety of SQL queries in order to find and output
# the amount of stops on each line color going in each direction. It also outputs
# the percentage that each line color and direction make up out of the total number of stops.
def colorPercentages(dbConn):
    dbCursor = dbConn.cursor()
    print("Number of Stops For Each Color By Direction")

    query = "select count(*) as Total_Stops from Stops"
    dbCursor.execute(query)
    row = dbCursor.fetchone();

    stopTotalNum = row[0]

    query = """select Color, Direction, count(Stop_Name) 
            from Lines join Stops 
            on Stops.Stop_ID=StopDetails.Stop_ID 
            join StopDetails on StopDetails.Line_ID=Lines.Line_ID 
            group by Color, Direction 
            order by Color asc, Direction asc"""
    dbCursor.execute(query)
    colorNums = dbCursor.fetchall();    

    for number in colorNums:
        percent = (number[2]/stopTotalNum)*100
        print(number[0], "going", number[1], ":", number[2],f"({percent:.2f}%)" )
    print()



# Command 6
#
# yearRidership
#
# Executes a variety of SQL queries in order to find and output
# the total ridership for each year of a specific station that
# has been inputted by the user. Can also plot results.
def yearRidership(dbConn):
    print()
    station_input = input("Enter a station name (wildcards _ and %): ")
    dbCursor = dbConn.cursor()

    query = """select Station_Name from Stations where Station_Name like ?"""
    dbCursor.execute(query,(station_input,))
    row = dbCursor.fetchall();

    if len(row) == 0:
        print("**No station found...")
        print()
        return
    elif len(row) > 1:
        print("**Multiple stations found...")
        print()
        return

    stationName = row[0][0]
    
    query = """select strftime('%Y', Ride_Date) AS Year, 
            sum(Num_Riders) from Stations join Ridership 
            on Ridership.Station_ID=Stations.Station_ID 
            where Station_Name = ? group by Year"""
    dbCursor.execute(query,(stationName,))
    yearData = dbCursor.fetchall();

    print("Yearly Ridership at", stationName)
    for year in yearData:
        print(year[0], ":", f"{year[1]:,}")

    print()
    plot_input = input("Plot? (y/n) ")
    print()

    if plot_input == 'y':
        x = []
        y = []

        for year in yearData:
            x.append(year[0])
            y.append(year[1])

        plt.xlabel("Year")
        plt.ylabel("Number of Riders")

        title = "Yearly Ridership at " + stationName + " Station"
        plt.title(title)

        ax = plt.gca()
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.ioff()
        plt.plot(x, y)
        plt.show()
    else:
        return



# Command 7
#
# findMonthData
#
# User enters a station name and a year and through the execution of various SQL
# queries the monthly ridership of that station for that specific year is output.
# Can also plot results.
def findMonthData(dbConn):
    print()
    station_input = input("Enter a station name (wildcards _ and %): ")
    dbCursor = dbConn.cursor()

    query = """select Station_Name from Stations where Station_Name like ?"""
    dbCursor.execute(query,(station_input,))
    row = dbCursor.fetchall();

    if len(row) == 0:
        print("**No station found...")
        print()
        return
    elif len(row) > 1:
        print("**Multiple stations found...")
        print()
        return

    stationName = row[0][0]

    year_input = input("Enter a year: ")

    query = """
            select strftime('%m', Ride_Date) as Month,
            sum(Num_Riders)
            from Stations
            join Ridership on Ridership.Station_ID=Stations.Station_ID
            where Station_Name = ? and strftime('%Y', Ride_Date) = ?
            group by Month;"""
    dbCursor.execute(query,(stationName,year_input,))
    monthData = dbCursor.fetchall();

    print("Monthly Ridership at", stationName, "for", year_input)
    for month in monthData:
        print(month[0] + "/" + year_input, ":", f"{month[1]:,}")

    print()
    plot_input = input("Plot? (y/n) ")
    print()

    if plot_input == 'y':
        x = []
        y = []

        for month in monthData:
            x.append(month[0])
            y.append(month[1])

        plt.xlabel("Month")
        plt.ylabel("Number of Riders")

        title = "Monthly Ridership at " + stationName + " Station " + "(" + year_input + ")"
        plt.title(title)

        plt.ioff()
        plt.plot(x, y)
        plt.show()
    else:
        return



# Command 8
#
# twoStationData
#
# User inputs a year to compare the daily ridership of that year for 
# two different stations whose names the user has also input. Results Can
# be plotted.
def twoStationData(dbConn):
    print()
    year_input = input("Year to compare against? ")
    dbCursor = dbConn.cursor()
    print()

    station1Input = input("Enter station 1 (wildcards _ and %): ")

    query = """select Station_ID, Station_Name from Stations where Station_Name like ?"""
    dbCursor.execute(query,(station1Input,))
    station1Info = dbCursor.fetchall();

    if len(station1Info) == 0:
        print("**No station found...")
        print()
        return
    elif len(station1Info) > 1:
        print("**Multiple stations found...")
        print()
        return

    print()
    station2Input = input("Enter station 2 (wildcards _ and %): ")
    dbCursor.execute(query,(station2Input,))
    station2Info = dbCursor.fetchall();

    if len(station2Info) == 0:
        print("**No station found...")
        print()
        return
    elif len(station2Info) > 1:
        print("**Multiple stations found...")
        print()
        return

    query = """select strftime('%Y-%m-%d', Ride_Date) as Day,
            sum(Num_Riders)
            from Stations
            join Ridership on Ridership.Station_ID=Stations.Station_ID
            where Station_Name = ? and strftime('%Y', Ride_Date) = ?
            group by Day
            """
    dbCursor.execute(query,(station1Info[0][1],year_input,))
    station1Dates = dbCursor.fetchall();

    print("Station 1:", station1Info[0][0], station1Info[0][1])
    for date in station1Dates[:5]:
        print(date[0], date[1])
    for date in station1Dates[-5:]:
        print(date[0], date[1])

    dbCursor.execute(query,(station2Info[0][1],year_input,))
    station2Dates = dbCursor.fetchall();

    print("Station 2:", station2Info[0][0], station2Info[0][1])
    for date in station2Dates[:5]:
        print(date[0], date[1])
    for date in station2Dates[-5:]:
        print(date[0], date[1])

    print()
    plot_input = input("Plot? (y/n) ")
    print()

    if plot_input == 'y':
        x1 = []
        x2 = []
        y1 = []
        y2 = []

        day = 1
        for date in station1Dates:
            x1.append(day)
            y1.append(date[1])
            day = day + 1

        day = 1
        for date in station2Dates:
            x2.append(day)
            y2.append(date[1])
            day = day + 1

        plt.xlabel("Day")
        plt.ylabel("Number of Riders")

        title = "Ridership Each Day of " + year_input
        plt.title(title)

        plt.ioff()
        plt.plot(x1, y1, label= station1Info[0][1])
        plt.plot(x2,y2, label= station2Info[0][1])
        plt.legend()
        plt.show()
    else:
        return



# Command 9
#
# findStationsNearby
# 
# The user inputs a latitude and longitude of their choosing
# and the function will then search and output using various SQl queries
# each station's name and coordinates that is within 1 mile
# of the user's chosen latitude and longitude. The results can be plotted on a map
# of Chicago.
def findStationsNearby(dbConn):
    dbCursor = dbConn.cursor()
    print()

    latitude = float(input("Enter a latitude: "))
    if latitude > 43 or latitude < 40:
        print("**Latitude entered is out of bounds...")
        print()
        return

    longitude = float(input("Enter a longitude: "))
    if longitude > -87 or longitude < -88:
        print("**Longitude entered is out of bounds...")
        print()
        return
    
    latDiff = 1.0/69.0
    longDiff = 1.0/51.0

    upperBoundLat = round(latitude + latDiff, 3)
    lowerBoundLat = round(latitude - latDiff, 3)
    upperBoundLong = round(longitude + longDiff, 3)
    lowerBoundLong = round(longitude - longDiff, 3)    

    query = """select distinct(Station_Name), Latitude, Longitude from Stops
            join Stations on Stations.Station_ID=Stops.Station_ID
            where Latitude > ? and Latitude < ? and Longitude > ? and Longitude < ?
            order by Station_Name asc """
    dbCursor.execute(query,(lowerBoundLat, upperBoundLat, lowerBoundLong, upperBoundLong,))
    stopsNearby = dbCursor.fetchall();

    if len(stopsNearby) == 0:
        print("**No stations found...")
        print()
        return

    print()
    print("List of Stations Within a Mile")
    for stop in stopsNearby:
        print(stop[0], ":", "(" + str(stop[1]) + ", " + str(stop[2]) + ")")

    print()
    plot_input = input("Plot? (y/n) ")
    print()

    if plot_input == 'y':
        x = []
        y = []

        for stop in stopsNearby:
            x.append(stop[2])
            y.append(stop[1])
          
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]

        plt.imshow(image, extent=xydims)
        plt.title("Stations Near You")
        plt.plot(x,y,'bo')

        for stop in stopsNearby:
            plt.annotate(stop[0], (stop[2], stop[1]))

        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()
    else:
        return
    

##################################################################  
#
# main
#

print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)

while True:    
    command = input('Please enter a command (1-9, x to exit): ')
    
    if(command == '1'):
        findStation(dbConn) 
    elif(command == '2'):
        findPercentages(dbConn)
    elif(command=='3'):
        weekdayRidership(dbConn)
    elif(command=='4'):
        lineAndDirection(dbConn)
    elif(command=='5'):
        colorPercentages(dbConn)
    elif(command=='6'):
        yearRidership(dbConn)
    elif(command=='7'):
        findMonthData(dbConn)
    elif(command=='8'):
        twoStationData(dbConn)
    elif(command=='9') :
        findStationsNearby(dbConn)
    elif(command=='x'):
        break
    else:
        print("**Error, unknown command, try again...")
        print()

#
# done
#
