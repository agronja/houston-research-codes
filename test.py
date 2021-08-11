#!/usr/bin/env python3
import os
import sys
import pprint
import gzip
import pickle
import networkx as nx
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from sklearn import metrics, datasets, svm
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def main():
	filename = "maxed-directed-weighted.p"
	directory = "pickled-final-files/"
	x = filename.split('.')[0] 
	title = x.split('-')
	# print("Using a(n)", " ".join(title), "graph...")
	y = []
	X = []
	fd = directory + filename
	cmSave = "confusion-matrix-files/" + x + ".png"
	rocSave = "ROC-files/" + x + ".png"
	crSave = "classification-report-files/" + x + ".png"
	theResults = pickle.load(open(fd, "rb"))
	for item in theResults:
		# if not certain_fams or item[0] in fams_to_test:
		y.append(item[0])
		X.append(item[1])

	classes = list(set(y))
	classes.sort()
	n_classes = len(classes)

	y_bin = label_binarize(y, classes=classes)

	# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)

	clf = OneVsRestClassifier(svm.SVC(kernel='linear', C=1, probability=True, random_state=0))
	# clf = OneVsRestClassifier(RandomForestClassifier(n_estimators=10, max_depth=2, random_state=0))

	# clf.fit(X_train, y_train)

	print(cross_val_score(clf, X, y_bin, cv=3))

	
		




if __name__ == '__main__':
	main()