# bo.zhang@ki.se
# precursor mass recalibration based on the first-pass Morpheus search
# spectral cloning based on TOPP feature map
# MGF generation

import sys
import os
import csv
import subprocess
import cPickle
import bz2
import tempfile

from multiprocessing import Process

import pandas
import numpy
# from sklearn.linear_model import LinearRegression, BayesianRidge
from pyearth import Earth  # rev. 2013-12-03 MARS with py-earth

import psmTheoretical


class NoneClf(object):
    def __init__(self):
        return

    def predict(self, p):
        return 0


def pickle_dump(obj, fn, p=2):
    f = bz2.BZ2File(fn, 'wb')
    f.write(cPickle.dumps(obj, p))
    f.close()
    return


def regression(fn):
    df = pandas.read_table(fn)
    df = df[df["Q-Value (%)"] < 1.0] # take only high confident identifications as 'lock masses'. 
    # df = df[df["Q-Value (%)"] == 0]
    
    theoretical_mz = []
    for i, x in df.iterrows():
        _, _, mz = psmTheoretical.calc_precursor_theoretical(x['Peptide Sequence'], int(x['Precursor Charge']))
        theoretical_mz.append(mz)
    df['Theoretical m/z'] = theoretical_mz
    df['Precursor Mass Error (ppm)'] = (df['Precursor m/z'] - df['Theoretical m/z']) * 1e6 / df['Theoretical m/z']
    X = numpy.array(zip(df['Precursor m/z'], df['Retention Time (minutes)'] * 60))
    y = df['Precursor Mass Error (ppm)']
    # clf = LinearRegression()
    # clf = BayesianRidge()
    clf = Earth()
    clf.fit(X, y)
    return clf


def load_feature_table(fn, features):
    table = []
    with open(fn, 'r') as fh:
        rd = csv.reader(fh, delimiter=',')
        for row in rd:
            if row[0] == 'FEATURE':
                _, rt, mz, _, chg, _, _, _, _, rtl, rtr = row
                table.append([float(mz), int(chg), float(rtl), float(rtr), float(rt)])
    table.sort(key=lambda x: x[3])
    sfn = os.path.splitext(os.path.basename(fn))[0]
    features[sfn] = table


def f(args):
    subprocess.check_call(args)


if __name__ == '__main__':
    sys.stderr.write("feature.csv   mzML   PSM.tsv   iso_width  threads\n")

    feature_fn = sys.argv[1]    # feature csv table exported from FeatureXML by TOPP. 
    mzml_fn = sys.argv[2]       # centroided MS/MS spectra in mzML, the same file which has been used in the first-pass database search.
    rawpsm_fn = sys.argv[3]     # first-pass database search result: Morpheus .PSMs.tsv file. 
    isolation = float(sys.argv[4]) / 2.0   # the total width of precursor isolation window.
    numproc = sys.argv[5]       # multi-threading text processing, MGF files need to be combined later. 

    sys.stderr.write( '\n'.join(sys.argv[1:6]))

    features = {}
    # with open(feature_fn) as fh:
    #     for fn in fh:
    #         load_feature_table(fn.rstrip(), features)

    load_feature_table(feature_fn, features)    # it is suggested to separately precess each LC-MS/MS experiment.
    clf = regression(rawpsm_fn)

    # dump_path = os.path.split(mzml_fn)[1] + '.dump'
    dump_path = tempfile.mkstemp()[1]
    pickle_dump((features, clf, isolation), dump_path)

    sys.stderr.write("\nRegression done.\n")

    exe_path = os.path.join(os.path.split(sys.argv[0])[0], '_mzml2mgf.py')  # path of the script for spectral cloning. 
    outpath = '-'.join(features.keys())

    jobs = []
    for i in range(int(numproc)):
        arg = ['python', exe_path, mzml_fn, dump_path, outpath, numproc, str(i)]
        p = Process(target=f, args=[arg])
        p.start()
        jobs.append(p)

    for p in jobs:
        p.join()