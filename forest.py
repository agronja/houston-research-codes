#!/usr/bin/env python3
import os
import sys
import pprint
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt

directory = "pickled-files/"

def forestClass(filename):
    families = []
    fvs = []
    fd = directory + filename
    figSave = "confusion-matrix-files/" + filename.split('.')[0] + ".png"
    theResults = pickle.load(open(fd, "rb"))
    for item in theResults:
        families.append(item[0])
        fvs.append(item[1])
    
    fv_train, fv_test, fam_train, fam_test = train_test_split(fvs, families, test_size=0.2)

    
    clf = RandomForestClassifier(n_estimators=100, max_depth=4)
    clf.fit(fv_train, fam_train)
    score = clf.score(fv_test, fam_test)
    fam_predict = clf.predict(fv_test)

    print(f"{filename}")

    metrics.plot_confusion_matrix(clf, fv_test, fam_test)
    title = filename.split('.')[0].split('-')
    plt.title(", ".join(title).title())
    plt.savefig(figSave)

    print(metrics.classification_report(fam_test, fam_predict, digits=3))
    print()
    

def main():

    for filename in os.listdir(directory):
        forestClass(filename)



if __name__ == '__main__':
    main()