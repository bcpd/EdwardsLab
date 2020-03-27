#!/usr/bin/python

# Download WHO geographic distribution of COVID-19 cases worldwide
# Source : European Centre for Disease Prevention and Control
# Plot cases and deaths for selected countries
# The downloaded spreadsheet is stored locally in Covid-19.csv
# To use cached local spreadsheet, use "-l" option
# Intermediate data for cases/deaths and also for each country are stored in relevant .csv files
# All plots can be aligned to :
#   First date of detection or death, in that country (default)
#   First date of detection in China, 2019-12-31 (-n)
# Data can be plotted as daily values (default) cumulative values (-c)
# Countries to plot and line colours are specified in the appropriate tables at the top of this file

# Dependencies : pandas, matplotlib, numpy, google-auth-httplib2, beautifulsoup4, xlrd


import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import urllib.request

from bs4 import BeautifulSoup


topLevelPage  = "https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide"
localFileName = "Covid-19.csv"

countries = ["China","Germany","Italy","United_Kingdom","United_States_of_America"]
colours   = ["red",  "black",  "green","blue",          "orange"]

# Extract cases and deaths and align day 0 to first date of detection or death
def extractAligned(covidData, country, dates, noAlignFlag):
    print("Country: " + country)

    countryData  = pd.DataFrame(index = dates)      # Create dataframe for country data

                    # Extract the data for the required country
                    # We need to copy it to the new countryData array so that dates are pre-pended back to 2019-12-31
    countryData_tmp = covidData[covidData["countriesAndTerritories"].str.match(country)]
    countryData_tmp = countryData_tmp.iloc[::-1]            # Invert table - top to bottom
    countryData[list(countryData_tmp.columns.values)] = countryData_tmp[list(countryData_tmp.columns.values)]
    countryData=countryData.fillna(0)                       # Replace NaN with 0

                                    # Fill columns : countriesAndTerritories geoId countryterritoryCode  popData2018
    countryData['countriesAndTerritories'] = countryData['countriesAndTerritories'].iloc[-1]
    countryData['geoId']                   = countryData['geoId'].iloc[-1]
    countryData['countryterritoryCode']    = countryData['countryterritoryCode'].iloc[-1]
    countryData['popData2018']             = countryData['popData2018'].iloc[-1]

                                    # Create cumulative cases column and cumulative deaths column - Rename column titles
    countryDataCS = countryData.cumsum(axis = 0)
    countryDataCS = countryDataCS.rename(columns={"cases": "casesCumulative", "deaths": "deathsCumulative"})

                                    # Copy cumulative columns to countryData
    countryData['casesCumulative']  = countryDataCS['casesCumulative']
    countryData['deathsCumulative'] = countryDataCS['deathsCumulative']

                                    # Replace NaN with 0
    countryData=countryData.fillna(0)

    outputFileName = country + ".csv"
    countryData.to_csv(outputFileName, index=True)

                                    # Print first data of cases
    dc = countryData.index[countryData['cases'] != 0].tolist()
    print("First Case            : " + str(dc[0]).replace(' 00:00:00',''))

                                    # Print first data of deaths
    dd = countryData.index[countryData['deaths'] != 0].tolist()
    print("First Death           : " + str(dd[0]).replace(' 00:00:00',''))

    totalCases=countryData['casesCumulative'].iloc[-1]
    totalDeaths=countryData['deathsCumulative'].iloc[-1]
    fatalityRate=totalDeaths*100./totalCases


    print('Total number of cases : ' + str(totalCases))
    print('Total number of deaths: ' + str(totalDeaths))
    print("Fatality rate         : %.2f %%" % (fatalityRate))
    print('')

                    # If we are not aligning first case or death then just return the data
    if noAlignFlag == True:
        return country, countryData, countryData;

                    # Align to first case or death by removing leading zeros and resetting index
                    # Get names of indexes for which column casesCumulative has value 0
    else:
                                    # Remove leading zeros from cases
        indexNames = countryData[ countryData['casesCumulative'] == 0 ].index
        extractedCases = countryData.drop(indexNames)
        extractedCases = extractedCases.reset_index()

                                    # Remove leading zeros from deaths
        indexNames = countryData[ countryData['deathsCumulative'] == 0 ].index
        extractedDeaths = countryData.drop(indexNames)
        extractedDeaths = extractedDeaths.reset_index()

        return country, extractedCases, extractedDeaths;


# main
def main(useCachedFileFlag, cumulativeResultsFlag, noAlignFlag, noPlotFlag):

    cachedFilePresentFlag = False

    try:
        f = open(localFileName)
        cachedFilePresentFlag = True
        f.close()
    except IOError:
        cachedFilePresentFlag = False


                                    # If cached file not present or we have requested to refresh then get the file
    if (cachedFilePresentFlag == False) or (useCachedFileFlag == False):
        resp = urllib.request.urlopen(topLevelPage)
        soup = BeautifulSoup(resp, "html.parser", from_encoding=resp.info().get_param('charset'))

        for link in soup.find_all('a', href=True):
            # print(link['href'])
            if ("csv" in link['href']):
                # print(link['href'])
                csvfileurl = link['href']

        if (csvfileurl):
            urllib.request.urlretrieve(csvfileurl, localFileName)
            cachedFilePresentFlag = True
            print("Cached file updated")
        else:
            print("Spreadsheet file not found on website")
            exit()

    numberOfCountries = len(countries)

    extractedCountry = {}           # Create empty dictionaries to store result data frames for each country
    extractedCases = {}
    extractedDeaths = {}

    if (cachedFilePresentFlag == True):
        covidData = pd.read_csv(localFileName, index_col=0, encoding="iso8859_1")
                    # Spreadsheet columns :
                    # dateRep	day	month	year	cases	deaths	countriesAndTerritories	geoId	countryterritoryCode	popData2018

        covidData=covidData.fillna(0)               # Replace NaN with 0

        clen = 0                    # For longest sequency
        dlen = 0

                                                    # Extract Chinese dates to create index - this allows for countries that do not have full data supplied
        dates_tmp = covidData[covidData["countriesAndTerritories"].str.match("China")]
        dates_tmp = dates_tmp.iloc[::-1]            # Invert table - top to bottom
        dates_tmp=dates_tmp.reset_index()
        dates=list(dates_tmp['dateRep'])

        countryIndex = 0
        for country in countries:
                                    # For each country - extract the aligned data
                                    # Data can be aligned on 2019-12-29 or first instance
            extractedCountry[countryIndex], extractedCases[countryIndex], extractedDeaths[countryIndex] = \
                extractAligned(covidData, country, dates, noAlignFlag)

            clen = np.maximum(clen, extractedCases[countryIndex].shape[0])
            dlen = np.maximum(dlen, extractedDeaths[countryIndex].shape[0])

            countryIndex = countryIndex+1

        if noPlotFlag == False:     # Plot the data
                                    # Select daily or cumulative results
            if (cumulativeResultsFlag == True):
                casesType  = 'casesCumulative'
                deathsType = 'deathsCumulative'
            else:
                casesType  = 'cases'
                deathsType = 'deaths'

                                    # Get last date in combinedCases
            lastDate = str(covidData.first_valid_index())
            lastDate = lastDate.replace(' 00:00:00','')

                                    # Plot results
            if (cumulativeResultsFlag == True):
                titleStr='Covid-19 Cumulative Cases: ' + str(lastDate)
            else:
                titleStr='Covid-19 Daily Cases: ' + str(lastDate)

            ax = plt.gca()          # Create plot - get current axis
            countryIndex = 0
            for country in countries:
                extractedCases[countryIndex].plot(kind='line',y=casesType,title=titleStr,label=extractedCountry[countryIndex],color=colours[countryIndex],ax=ax)
                countryIndex = countryIndex+1
            plt.show()

            if (cumulativeResultsFlag == True):
                titleStr='Covid-19 Cumulative Deaths: ' + str(lastDate)
            else:
                titleStr='Covid-19 Daily Deaths: ' + str(lastDate)

            ax = plt.gca()          # Create plot - get current axis
            countryIndex = 0
            for country in countries:
                extractedDeaths[countryIndex].plot(kind='line',y=deathsType,title=titleStr,label=extractedCountry[countryIndex],color=colours[countryIndex],ax=ax)
                countryIndex = countryIndex+1
            plt.show()

    else:
        print("Cached spreadsheet file not found on computer")
        exit()


if __name__ == '__main__':
    useCachedFileFlag       = False
    cumulativeResultsFlag   = False
    noAlignFlag             = False
    noPlotFlag              = False

    if len(countries) != len(colours):
        print("The number of colours must equal the number of countries")
        exit()


    parser = argparse.ArgumentParser(description='Covid-19 Visualizer')
    parser.add_argument("-c", "--cumulative", action="store_true", help="Display cumulative results")
    parser.add_argument("-l", "--local",      action="store_true", help="Use local cached Covid-19.csv")
    parser.add_argument("-n", "--noalign",    action="store_true", help="Do not align first instance dates - all graphs start 2019-12-31")
    parser.add_argument("-q", "--quiet",      action="store_true", help="Quiet - Do not plot graphs")
    args = parser.parse_args()

    if (args.cumulative):
        cumulativeResultsFlag = True
        print("Cumulative Results = True")

    if (args.local):
        useCachedFileFlag = True
        print("Use cached file = True")

    if (args.noalign):
        noAlignFlag = True
        print("Do not align first instance date = True")

    if (args.quiet):
        noPlotFlag = True
        print("Do not plot graphs = True")

    main(useCachedFileFlag, cumulativeResultsFlag, noAlignFlag, noPlotFlag)
