import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from os import listdir
from os.path import isfile, join


splits = ["CLIA_Track", "General_Track", "Inv_Track", "PBE_BV_Track", "PBE_SLIA_Track"]

def main(p):#
    names = [f for f in listdir("csv") if isfile(join("csv", f))]
    names = ["csv/"+n for n in names]
    data = [pd.read_csv(f) for f in names]
    data_split = []

    for frame in data:
        data_split.append(split_pd(frame, splits))

    for i in range(len(data_split)):
        s = names[i] + "\n"
        c = 0
        for j in range(len(splits)):
            c += np.sum(data_split[i][j]['time'].to_numpy())
            all_pass = data_split[i][j][data_split[i][j]['pass'] == 1.0]
            if len(all_pass.index) == 0:
                break
            s += str(r(len(all_pass.index) / len(data_split[i][j]), 100)) + "\t|\t"
            s += str(len(all_pass.index)) +"/" + str(len(data_split[i][j])) + "\t|\t"
            s += str(r(np.mean(all_pass['time'].to_numpy()), 100)) + "\t|\t" + str(r(np.mean(data_split[i][j]['time'].to_numpy()), 100))
            s += "\t|\t" + str(np.sum(data_split[i][j]['time'].to_numpy()))
            s += "\t|\t" + splits[j] + "\n"
        s += "Total Time: " + str(c) + "\n"
        s += "------------------------\n"
        print(s)
    print("------------------------\n\n")
    test_count = len(data[0].index)
    set_count = len(data)


    best = data[0].copy(deep=True)
    best['solver'] = names[0]
    c = 0
    for i in range(test_count):
        cur = best.iloc[i]
        for j in range(1, set_count):
            new = data[j].iloc[i]
            if new['pass'] == 1.0 and new['time'] < cur['time'] or (cur['pass'] != 1.0 and new['pass'] == 1.0):
                c += 1
                new['solver'] = names[j]
                cur = new
        best.iloc[i] = cur



    best_split = split_pd(best, splits)
    s = "best possible \n"
    c = 0
    for j in range(len(splits)):
        c += np.sum(best_split[j]['time'].to_numpy())
        all_pass = best_split[j][best_split[j]['pass'] == 1.0]
        if len(all_pass.index) == 0:
            break
        s += str(r(len(all_pass.index) / len(best_split[j]), 100)) + "\t|\t"
        s += str(len(all_pass.index)) +"/" + str(len(best_split[j])) + "\t|\t"
        s += str(r(np.mean(all_pass['time'].to_numpy()), 100)) + "\t|\t" + str(r(np.mean(best_split[j]['time'].to_numpy()), 100))
        s += "\t|\t" + str(np.sum(best_split[j]['time'].to_numpy()))
        s += "\t|\t" + splits[j]
        s += "\n"
    s += "------------------------\n\nTotal Time: "
    s += str(c)
    best.to_csv("output.csv", index=False)
    print(s)

def r(v, n):
    return np.round(v*n)/n


def split_pd(data, splits):
    new = []
    for s in splits:
        new.append(data[data['dir'].str.contains(s)])
    return new



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
