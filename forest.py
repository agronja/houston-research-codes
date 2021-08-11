#!/usr/bin/env python3
import os
import sys
import pprint
import pickle
from multiprocessing import Pool
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from sklearn import metrics, svm
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import seaborn as sns
import pandas as pd

directory = "pickled-final-files/"
randState = 0
certain_fams = False

def forestClass(filename):
    x = filename.split('.')[0] 
    title = x.split('-')
    # print("Using a(n)", " ".join(title), "graph...")
    families = []
    fvs = []
    fd = directory + filename
    cmSave = "confusion-matrix-files/" + x + ".png"
    rocSave = "ROC-files/" + x + ".png"
    crSave = "classification-report-files/" + x + ".png"
    theResults = pickle.load(open(fd, "rb"))
    fams_to_test = ['klez', 'sytro', 'mira', 'browsefox', 'fireseria', 'multiplug', 'expiro']
    for item in theResults:
        if not certain_fams or item[0] in fams_to_test:
            families.append(item[0])
            fvs.append(item[1])
    
    classes = list(set(families))
    classes.sort()
    n_classes = len(classes)

    fam_bin = label_binarize(families, classes=classes)

    # SVM classifier first
    print("Creating SVM classifier...  ", end="\r")
    classifier = OneVsRestClassifier(svm.SVC(kernel='linear', probability=True, random_state=randState))
    scores_svm = cross_val_score(classifier, fvs, families, cv=5)

    # label_binarize to 'families'
    fv_train, fv_test, fam_train, fam_test = train_test_split(fvs, fam_bin, test_size=0.2, random_state=randState)
    classifier.fit(fv_train, fam_train)
    fam_score = classifier.decision_function(fv_test)

    print("Creating ROC curve...       ", end="\r")
    cm = plt.get_cmap('tab20')
    cNorm = colors.Normalize(vmin=0, vmax=n_classes)
    scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
    _, ax = plt.subplots()
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(n_classes)])
    fpr, tpr, roc_auc = dict(), dict(), dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = metrics.roc_curve(fam_test[:, i], fam_score[:, i])
        roc_auc[i] = metrics.auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], lw=1, label='%s ROC curve (area = %0.4f)' % (classes[i].title(), roc_auc[i]))
    
    plt.plot([0,1], [0,1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    fpr["avg"], tpr["avg"], _ = metrics.roc_curve(fam_test.ravel(), fam_score.ravel())
    roc_auc["avg"] = metrics.auc(fpr["avg"], tpr["avg"])
    plt.plot(fpr["avg"], tpr["avg"], lw=2, label='Avg ROC curve (area = %0.4f)' % (roc_auc["avg"]))

    h, l = ax.get_legend_handles_labels()
    handles, labels = [], []
    hl = sorted(zip(l, h))
    idx_avg = 0
    for idx, asdf in enumerate(hl):
        if asdf[0][:13] == "Avg ROC curve":
            idx_avg = idx
            continue
        handles.append(asdf[1])
        labels.append(asdf[0])
    handles.append(hl[idx_avg][1])
    labels.append(hl[idx_avg][0])

    plt.title(", ".join(title).title())
    lgd = plt.legend(handles, labels, title='Legend', bbox_to_anchor=(1.05, 1), loc="best")
    plt.savefig("svm-files/" + rocSave, bbox_extra_artists=(lgd,), bbox_inches='tight')

    # Confusion Matrix
    print("Creating confusion matrix...", end="\r")
    fam_predict = classifier.predict(fv_test)
    disp = metrics.confusion_matrix(fam_test.argmax(axis=1), fam_predict.argmax(axis=1))
    _, ax = plt.subplots()
    sns.heatmap(disp, annot=True, cmap=plt.cm.YlOrRd, fmt='d')

    _, labels = plt.xticks()
    for idx, x in enumerate(labels):
        x.set_text(classes[idx])
    
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    plt.setp(labels, rotation=40, horizontalalignment="right")
    _, labels = plt.yticks()
    plt.setp(labels, rotation=0)
    plt.title(", ".join(title).title())
    plt.xlabel('Predicted label')
    plt.ylabel('True label')
    plt.tight_layout()
    plt.savefig("svm-files/" + cmSave)

    print("Creating classification report...", end="\r")
    cr = metrics.classification_report(fam_test, fam_predict, digits=3, target_names=classes, output_dict=True, zero_division=0)

    print("Using a(n)", " ".join(title).title(), "graph:                             \n", metrics.classification_report(fam_test, fam_predict, digits=3, target_names=classes, zero_division=0))
    plt.figure()
    sns.heatmap(pd.DataFrame(cr).iloc[:-1,:].T, annot=True)
    plt.title(", ".join(title).title())
    plt.tight_layout()
    plt.savefig("svm-files/" + crSave)

    # print("SVM done.")
    
    print("Creating random forest...   ", end="\r")
    fv_train, fv_test, fam_train, fam_test = train_test_split(fvs, families, test_size=0.2, random_state=randState)
    fam_test_bin = label_binarize(fam_test, classes=classes)

    clf = OneVsRestClassifier(RandomForestClassifier(n_estimators=500, max_depth=5, criterion="entropy", min_samples_split=5, random_state=randState))
    # OneVsRestClassifier with RF. Use predict_probat
    clf.fit(fv_train, fam_train)
    fam_predict = clf.predict(fv_test)
    fam_score = clf.predict_proba(fv_test)
    scores_rf = cross_val_score(clf, fvs, families, cv=5)

    # Confusion Matrix
    print("Creating confusion matrix...", end="\r")
    metrics.plot_confusion_matrix(clf, fv_test, fam_test, cmap=plt.cm.YlOrRd)
    plt.title(", ".join(title).title())
    
    _, labels= plt.xticks()
    plt.setp(labels, rotation=40, horizontalalignment='right')
    plt.tight_layout()
    plt.savefig("rf-files/" + cmSave)
    
    
    # ROC Curve
    print("Creating ROC curve...       ", end="\r")
    cm = plt.get_cmap('tab20')
    cNorm = colors.Normalize(vmin=0, vmax=n_classes)
    scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
    _, ax = plt.subplots()
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(n_classes)])
    
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    

    for i in range(n_classes):
        fpr[i], tpr[i], _ = metrics.roc_curve(fam_test_bin[:, i], fam_score[:, i])
        roc_auc[i] = metrics.auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], lw=1, label='%s ROC curve (area = %0.4f)' % (classes[i].title(), roc_auc[i]))
    
    plt.plot([0,1], [0,1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    fpr["avg"], tpr["avg"], _ = metrics.roc_curve(fam_test_bin.ravel(), fam_score.ravel())
    roc_auc["avg"] = metrics.auc(fpr["avg"], tpr["avg"])
    plt.plot(fpr["avg"], tpr["avg"], lw=2, label='Avg ROC curve (area = %0.4f)' % (roc_auc["avg"]))

    h, l = ax.get_legend_handles_labels()
    handles, labels = [], []
    hl = sorted(zip(l, h))
    idx_avg = 0
    for idx, asdf in enumerate(hl):
        if asdf[0][:13] == "Avg ROC curve":
            idx_avg = idx
            continue
        handles.append(asdf[1])
        labels.append(asdf[0])
    handles.append(hl[idx_avg][1])
    labels.append(hl[idx_avg][0])

    plt.title(", ".join(title).title())
    lgd = plt.legend(handles, labels, title='Legend', bbox_to_anchor=(1.05, 1), loc="best")
    plt.savefig("rf-files/" + rocSave, bbox_extra_artists=(lgd,), bbox_inches='tight')
    

    # Classification report
    print("Creating classification report...", end="\r")
    cr = metrics.classification_report(fam_test, fam_predict, digits=3, output_dict=True, zero_division=0)

    print("Using a(n)", " ".join(title).title(), "graph:                             \n", metrics.classification_report(fam_test, fam_predict, digits=3, zero_division=0), f"\n\nSVM Cross-val score: {scores_svm}\nRandom Forest Cross-val score: {scores_rf}\n")
    plt.figure()
    sns.heatmap(pd.DataFrame(cr).iloc[:-1,:].T, annot=True)
    plt.title(", ".join(title).title())
    plt.tight_layout()
    plt.savefig("rf-files/" + crSave)



    

def main():

    global directory
    global randState
    global certain_fams


    arguments = sys.argv[1:]
    
    while arguments and arguments[0].startswith('-'):
        argument = arguments.pop(0)
        if argument == '-d':
            directory = arguments.pop(0)
        elif argument == '-r':
            randState = int(arguments.pop(0))
        elif argument == '-c':
            certain_fams = True
    
    p = Pool(6)

    p.map(forestClass, os.listdir(directory))




if __name__ == '__main__':
    main()