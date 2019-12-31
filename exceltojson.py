import xlrd
import json
import os
os.chdir("./tables")
files = os.listdir()
for oneFile in files:
    if (oneFile.endswith(".xlsx")):
        data = xlrd.open_workbook(oneFile)
        table = data.sheet_by_index(0)
        nrows = table.nrows
        ncols = table.ncols

        varNames = []
        dataTypes = []
        results = []
        for row in range(nrows):
            oneResult = {}
            for col in range(ncols):
                #first row is var names
                #2nd row is data type
                if row == 0:
                    varNames.append(table.cell(row,col).value)
                    continue
                if row == 1:
                    dataTypes.append(table.cell(row,col).value)
                    continue
                oneData = table.cell(row,col).value
                varName = varNames[col]
                dataType = dataTypes[col]
                if dataType == "int":
                    oneData = int(oneData)
                oneResult[varName] = oneData
            if row != 0 and row != 1:
                results.append(oneResult)
                
        jsonStr = json.dumps(results,indent=4)
        name = data.sheet_names()[0] + ".json"
        os.chdir("../configs")
        with open(name,"w",encoding="utf-8") as f: 
            f.write(jsonStr)
        print(name + " convert success")
        os.chdir("../tables")