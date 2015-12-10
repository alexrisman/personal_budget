#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv

with open('tradesComb.csv', 'rb') as f:
    reader = csv.reader(f)
    rowsArray = list(reader)

    pnlLow = {}
    pnlAvg = {}
    pnlCount = {}
    for i in range(1, len(rowsArray)):
        print i
        if rowsArray[i][1] == "": continue
        pnl = float(rowsArray[i][4]) - float(rowsArray[i][2])
        if pnl <= 0: continue
        if rowsArray[i][1] in pnlLow:
            if pnl < pnlLow[rowsArray[i][1]]:
                pnlLow[rowsArray[i][1]] = pnl
        else:
            pnlLow[rowsArray[i][1]] = pnl

        if rowsArray[i][1] in pnlAvg:
            pnlAvg[rowsArray[i][1]] += pnl
            pnlCount[rowsArray[i][1]] += 1
        else:
            pnlAvg[rowsArray[i][1]] = pnl
            pnlCount[rowsArray[i][1]] = 1

    tradePnLFile = open("tradePnL.csv", "w")
    tradePnLFile.write("Product,PnLLow,PnLAvg,Count\n")
    for product in pnlLow:
        tradePnLFile.write(product + "," + str(pnlLow[product]) + "," + str(pnlAvg[product] / float(pnlCount[product])) + "," + str(pnlCount[product]) + "\n")
    tradePnLFile.close()