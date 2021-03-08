#!/usr/bin/python

# -*- coding: utf-8 -*-

# Import libraries
import sys
import os
import numpy as np
import pandas as pd
import pdb

# import logging

# Local function and classes
class Table:

    def __init__(self, path):
        
        # Attributes
        self.path = path
        self.table = None

        # Read table
        self.readFromPath()
    
    def readFromPath(self):

        try:
            self.table = pd.read_csv(self.path, sep="\t", header=0)
        
        except: 
            print(f"** Error when reading {self.path}")
            print()
            sys.exit(1)

class CombinedTable():

    def __init__(self):
        # Attributes
        self.tableDict = {}


    def buildMidPoint(self, tableObject):
        midPointsListOfLists = [table.table.iloc[:, 0].to_list() for table in tableObject]
        midPointsArray = np.array([j for i in midPointsListOfLists for j in i])
        midPointsArray = np.sort(midPointsArray)
        self.tableDict['midpoint'] = np.unique(np.round(midPointsArray, 5))

    def addCount(self, table, index):

        # when midpoint is not present, calculate from previous and next in a weighted way
        interpol = lambda x1,x3,m1,m2,m3 : x1 + (x3-x1)*(m2-m1)/(m3-m1)

        # Extract columns from input table
        midpointsTable = np.round(table.iloc[:, 0].to_numpy(), 5)
        countsTable = table.iloc[:, 1].to_numpy()

        # Array with new count of input table
        countsTableNew = np.array([], dtype="float64")

        for Ni, mid in enumerate(self.tableDict['midpoint']):

            # if midpoint in combined table is lower than the lowest of input table, write 0
            if mid < midpointsTable[0]:
                countsTableNew = np.append(countsTableNew, 0)
                continue
            
            # if midpoint in combined table is greater than the gratest of input table, write 0
            if mid > midpointsTable[-1]:
                countsTableNew = np.append(countsTableNew, 0)
                continue
            
            
            # if it is in middle, calculate:
                # if it is exactly, take it
            if mid in midpointsTable:
                countsTableNew = np.append(countsTableNew, countsTable[mid==midpointsTable])
                continue

                # if it is not exactly, calculate
            else:
                m3_index = np.where(mid == np.sort(np.append(midpointsTable, mid)))[0][0]
                m1_index = m3_index - 1
                m3 = midpointsTable[m3_index]
                m1 = midpointsTable[m1_index]
                x3 = countsTable[m3_index]
                x1 = countsTable[m1_index]

                if x1==x3:
                    countsTableNew = np.append(countsTableNew, x1)
                    continue

                countsTableNew = np.append(countsTableNew, interpol(x1,x3,m1,mid,m3))
        
        self.tableDict[f"count_{index}"] = np.round(countsTableNew, 5)

    def writeTable(self):
        pd.DataFrame(self.tableDict).to_csv("combinedTable.tsv", index=False, sep="\t")

# Main function
def main():
    
    fileList = [i for i in sys.argv[1:]]

    # If no file is introduced, get it from terminal
    if len(fileList) == 0:
        
        while True:
            try:
                nFiles = int(input("** Enter number of files that will be combined: "))
                break
            
            except:
                print("** Error. Please, try again.")
        
        i = 0
        while i < nFiles:
            iFile = str(input(f"** Enter path to file {i+1}: "))

            if not os.path.isfile(iFile):
                print("** Introduced file does not exist. Please try again.")
                continue

            fileList.append(iFile)
            i += 1
    
    # Read tables from fileList
    tableObject = [Table(i) for i in fileList]

    # Generate combined table
    combinedTable = CombinedTable()

    # Generate first column containing midpoint
    combinedTable.buildMidPoint(tableObject)

    # Add columns
    [combinedTable.addCount(table.table, os.path.splitext(fileList[i])[0]) for i, table in enumerate(tableObject)]

    # Write output table
    combinedTable.writeTable()


if __name__ == "__main__":

    main()