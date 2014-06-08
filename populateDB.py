import csv
from model import ATM


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

                )

            p.save()


path_prefix = "DataScript/ATMs_in_brampton/"
populateDB("RBC", path_prefix + "RBC/positions.csv")
populateDB("CIBC", path_prefix + "CIBC/positions.csv")
populateDB("BMO", path_prefix + "BMO/positions.csv")
populateDB("Scotia", path_prefix + "Scotia/positions.csv")
populateTD("TD", path_prefix + "TD/positions.csv")
