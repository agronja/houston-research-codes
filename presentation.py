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

def main():

    directory = "pickled-final-files/"
    randState = 0
    certain_fams = False
    filename = "unweighted-undirected.p"

    x = filename.split('.')[0]
    title = x.split('-')

    families = []
    fvs = []
    fd = directory + filename
    saveDir = "presentation-files/"

    theResults = pickle.load(open(fd, "rb"))
    for item in theResults:
        families.append(item[0])
        fvs.append(item[1])
    
    classes = list(set(families))
    classes.sort()
    n_classes = len(classes)

    print("Creating classifiers...     ", end="\r")
    classifierSVC = svm.SVC(kernel='linear', probability=True, random_state=randState)
    classifierSVCOVR = OneVsRestClassifier(classifierSVC)
    clfRF = RandomForestClassifier(n_estimators=500, max_depth=5, criterion="entropy", min_samples_split=5, random_state=randState)
    clfRFOVR = OneVsRestClassifier(clfRF)

    fv_train, fv_test, fam_train, fam_test = train_test_split(fvs, families, test_size=0.2, random_state=randState)
    fam_test_bin = label_binarize(fam_test, classes=classes)

    print("Training classifiers (1)...     ", end="\r")
    classifierSVC.fit(fv_train, fam_train)
    scoreSVC = classifierSVC.decision_function(fv_test)
    predictSVM = classifierSVC.predict(fv_test)
    print("Training classifiers (2)...     ", end="\r")
    classifierSVCOVR.fit(fv_train, fam_train)
    scoreSVCOVR = classifierSVCOVR.decision_function(fv_test)
    predictSVMOVR = classifierSVCOVR.predict(fv_test)
    print("Training classifiers (3)...     ", end="\r")
    clfRF.fit(fv_train, fam_train)
    scoreRF = clfRF.predict_proba(fv_test)
    predictRF = clfRF.predict(fv_test)
    print("Training classifiers (4)...     ", end="\r")
    clfRFOVR.fit(fv_train, fam_train)
    scoreRFOVR = clfRFOVR.predict_proba(fv_test)
    predictRFOVR = clfRFOVR.predict(fv_test)


    cm = plt.get_cmap('tab20')
    cNorm = colors.Normalize(vmin=0, vmax=n_classes)
    scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)

    print("Creating ROC curve (1)...   ", end="\r")
    _, ax = plt.subplots()
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(n_classes)])
    fpr, tpr, roc_auc = dict(), dict(), dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = metrics.roc_curve(fam_test_bin[:, i], scoreSVC[:, i])
        roc_auc[i] = metrics.auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], lw=1, label='%s ROC curve (area = %0.4f)' % (classes[i].title(), roc_auc[i]))
    
    plt.plot([0,1], [0,1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    fpr["avg"], tpr["avg"], _ = metrics.roc_curve(fam_test_bin.ravel(), scoreSVC.ravel())
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
    plt.savefig(saveDir + "ROC_SVM.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

    print("Creating ROC curve (2)...   ", end="\r")
    _, ax = plt.subplots()
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(n_classes)])
    fpr, tpr, roc_auc = dict(), dict(), dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = metrics.roc_curve(fam_test_bin[:, i], scoreSVCOVR[:, i])
        roc_auc[i] = metrics.auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], lw=1, label='%s ROC curve (area = %0.4f)' % (classes[i].title(), roc_auc[i]))
    
    plt.plot([0,1], [0,1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    fpr["avg"], tpr["avg"], _ = metrics.roc_curve(fam_test_bin.ravel(), scoreSVCOVR.ravel())
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
    plt.savefig(saveDir + "ROC_SVM_OVR.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

    print("Creating ROC curve (3)...   ", end="\r")
    _, ax = plt.subplots()
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(n_classes)])
    fpr, tpr, roc_auc = dict(), dict(), dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = metrics.roc_curve(fam_test_bin[:, i], scoreRF[:, i])
        roc_auc[i] = metrics.auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], lw=1, label='%s ROC curve (area = %0.4f)' % (classes[i].title(), roc_auc[i]))
    
    plt.plot([0,1], [0,1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    fpr["avg"], tpr["avg"], _ = metrics.roc_curve(fam_test_bin.ravel(), scoreRF.ravel())
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
    plt.savefig(saveDir + "ROC_RF.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

    print("Creating ROC curve (4)...   ", end="\r")
    _, ax = plt.subplots()
    ax.set_prop_cycle(color=[scalarMap.to_rgba(i) for i in range(n_classes)])
    fpr, tpr, roc_auc = dict(), dict(), dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = metrics.roc_curve(fam_test_bin[:, i], scoreRFOVR[:, i])
        roc_auc[i] = metrics.auc(fpr[i], tpr[i])
        plt.plot(fpr[i], tpr[i], lw=1, label='%s ROC curve (area = %0.4f)' % (classes[i].title(), roc_auc[i]))
    
    plt.plot([0,1], [0,1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    fpr["avg"], tpr["avg"], _ = metrics.roc_curve(fam_test_bin.ravel(), scoreRFOVR.ravel())
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
    plt.savefig(saveDir + "ROC_RF_OVR.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

    print("Creating confusion matrix (1)...", end="\r")
    metrics.plot_confusion_matrix(classifierSVC, fv_test, fam_test, cmap=plt.cm.YlOrRd)
    plt.title(", ".join(title).title())

    _, labels = plt.xticks()
    plt.setp(labels, rotation=40, horizontalalignment='right')
    plt.tight_layout()
    plt.savefig(saveDir + "CM_SVC.png")

    print("Creating confusion matrix (2)...", end="\r")
    metrics.plot_confusion_matrix(classifierSVCOVR, fv_test, fam_test, cmap=plt.cm.YlOrRd)
    plt.title(", ".join(title).title())

    _, labels = plt.xticks()
    plt.setp(labels, rotation=40, horizontalalignment='right')
    plt.tight_layout()
    plt.savefig(saveDir + "CM_SVC_OVR.png")

    print("Creating confusion matrix (3)...", end="\r")
    metrics.plot_confusion_matrix(clfRF, fv_test, fam_test, cmap=plt.cm.YlOrRd)
    plt.title(", ".join(title).title())

    _, labels = plt.xticks()
    plt.setp(labels, rotation=40, horizontalalignment='right')
    plt.tight_layout()
    plt.savefig(saveDir + "CM_RF.png")

    print("Creating confusion matrix (4)...", end="\r")
    metrics.plot_confusion_matrix(clfRFOVR, fv_test, fam_test, cmap=plt.cm.YlOrRd)
    plt.title(", ".join(title).title())

    _, labels = plt.xticks()
    plt.setp(labels, rotation=40, horizontalalignment='right')
    plt.tight_layout()
    plt.savefig(saveDir + "CM_RF_OVR.png")

    print("Creating classification report (1)...", end="\r")
    cr = metrics.classification_report(fam_test, predictSVM, digits=3, output_dict=True, zero_division=0)
    plt.figure()
    sns.heatmap(pd.DataFrame(cr).iloc[:-1,:].T, annot=True)
    plt.title(", ".join(title).title())
    plt.tight_layout()
    plt.savefig(saveDir + "CR_SVM.png")

    print("Creating classification report (2)...", end="\r")
    cr = metrics.classification_report(fam_test, predictSVMOVR, digits=3, output_dict=True, zero_division=0)
    plt.figure()
    sns.heatmap(pd.DataFrame(cr).iloc[:-1,:].T, annot=True)
    plt.title(", ".join(title).title())
    plt.tight_layout()
    plt.savefig(saveDir + "CR_SVM_OVR.png")

    print("Creating classification report (3)...", end="\r")
    cr = metrics.classification_report(fam_test, predictRF, digits=3, output_dict=True, zero_division=0)
    plt.figure()
    sns.heatmap(pd.DataFrame(cr).iloc[:-1,:].T, annot=True)
    plt.title(", ".join(title).title())
    plt.tight_layout()
    plt.savefig(saveDir + "CR_RF.png")

    print("Creating classification report (4)...", end="\r")
    cr = metrics.classification_report(fam_test, predictRFOVR, digits=3, output_dict=True, zero_division=0)
    plt.figure()
    sns.heatmap(pd.DataFrame(cr).iloc[:-1,:].T, annot=True)
    plt.title(", ".join(title).title())
    plt.tight_layout()
    plt.savefig(saveDir + "CR_RF_OVR.png")

    print("Checking cross-val scores (1)...    ", end="\r")
    cvscoreSVM = cross_val_score(classifierSVC, fvs, families, cv=10)
    print(cvscoreSVM)

    print("Checking cross-val scores (2)...    ", end="\r")
    cvscoreSVMOVR = cross_val_score(classifierSVCOVR, fvs, families, cv=10)
    print(cvscoreSVMOVR)

    print("Checking cross-val scores (3)...    ", end="\r")
    cvscoreRF = cross_val_score(clfRF, fvs, families, cv=10)
    print(cvscoreRF)

    print("Checking cross-val scores (4)...    ", end="\r")
    cvscoreRFOVR = cross_val_score(clfRFOVR, fvs, families, cv=10)
    print(cvscoreRFOVR)

if __name__ == '__main__':
    main()