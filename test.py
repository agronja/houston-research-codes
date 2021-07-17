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
		
	print(families)
	print(fvs)

def main():
	global directory
	arguments = sys.argv[1:]
	if arguments:
		directory = sys.argv[1]
	for filename in os.listdir(directory):
		forestClass(filename)
		break

if __name__ == '__main__':
	main()