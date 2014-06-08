import csv

def populateDB(owner, csvFileName):
    with open(csvFileName, 'r') as csvFile:
        mrReader = csv.reader(csvFile, delimiter = ',', quotechar = '"')
        next(reader, None)  # skip the headers
        for row in mrReader:
            p = ATM(
                owner = owner
                address = row[3]
                lat = row[0]
                lon = row[1]
            p.save


populateDB("RBC", "RBC/positions.csv")
populateDB("CIBC", "CIBC/positions.csv")
populateDB("BMO", "BMO/positions.csv")
populateDB("Scotia", "Scotia/positions.csv")
populateTD("TD", "TD/positions.csv")
