# Bo.Zhang@ki.se
# the parallel worker script for mass recalibration and MGF generation
# DO NOT RUN IT DIRECTLY

import sys
import os
import re
import cPickle
import bz2
import gzip
import lxml.etree
import xml.etree
import pymzml


MS1_Precision = 1e-5
MS2_Precision = 2e-5

def pickle_load(fn):
    f = bz2.BZ2File(fn, 'rb')
    tmps = ""
    while 1:
        data = f.read()
        if data == "":
            break
        tmps += data
    obj = cPickle.loads(tmps)
    f.close()
    return obj


def main(mzml, dump, outpath, spliter, indexer):
    if mzml.endswith('.gz'):
        fh = gzip.open(mzml)
    else:
        fh = open(mzml)
    source_file_dict = {}
    e = lxml.etree.iterparse(fh)
    for _, ee in e:
        if ee.tag.count("sourceFileList"):
            for sf in ee.getchildren():
                source_file_dict[sf.get('id')] = sf.get('name')
            break

    outpath = "%s.%d.mgf" % (outpath, indexer)
    sys.stdout = open(outpath, 'w')
    speciter = pymzml.run.Reader(mzml)
    features, clf, isolation = pickle_load(dump)
    timescale = 0
    sref = None
    try:
        for spec in speciter:
            element = spec.xmlTree.next()
            title = element.get('id')
            idx = element.get('index')
            sref = element.get('sourceFileRef')
            if not timescale:
                xmltext = xml.etree.ElementTree.tostring(element)
                if xmltext.count(r'unitName="second"'):
                    timescale = 1
                else:
                    timescale = 60
            if sref:
                sfn = os.path.splitext(source_file_dict[sref])[0]
            else:
                sfn = os.path.splitext(outpath.replace('.mgf', ''))[0]

            if not features.has_key(sfn):
                continue

            if spec['ms level'] == 2.0 and idx and int(idx) % spliter == indexer:
                try:
                    rt = float(spec['scan time']) * timescale
                except:
                    continue

                for p in spec['precursors']:
                    pmz = float(p['mz'])
                    try:
                        pz = int(p['charge'])
                    except:
                        pz = 0

                    featured = False
                    peaks = sorted(filter(lambda x: x[1], spec.centroidedPeaks), key=lambda i: i[0])

                    for f in features[sfn]:
                        fmz, fz, frt_left, frt_right, frt = f
                        if frt_left < rt < frt_right and abs(pmz - fmz) < isolation:
                            if abs(pmz - fmz) / pmz <= MS1_Precision: 
                                featured = True
                            print 'BEGIN IONS'
                            print 'TITLE=index:%s[%d:%f:%f]' % (idx, features[sfn].index(f), fmz, frt)
                            print 'RTINSECONDS=%f' % rt
                            print 'PEPMASS=%f' % (fmz - fmz * clf.predict([[fmz, frt]]) * 1e-6 )
                            print 'CHARGE=%d+' % fz
                            print 'USER00=%s:%s' % (sfn, title)
                            print 'USER01=[%f:%d]' % (pmz, pz)
                            print 'USER02=delta:%f' % (fmz - pmz)
                            for a, b in peaks:
                                print a, b
                            print 'END IONS\n'

                    if featured == False and pz > 1:
                        print 'BEGIN IONS'
                        print 'TITLE=index:%s[-:%f:%f]' % (idx, pmz, rt)
                        print 'RTINSECONDS=%f' % rt
                        print 'PEPMASS=%f' % (pmz - pmz * clf.predict([[pmz, rt]]) * 1e-6)
                        print 'CHARGE=%d+' % pz
                        print 'USER00=%s:%s' % (sfn, title)
                        for a, b in peaks:
                            print a, b
                        print 'END IONS\n'
    except KeyError:
        pass

if __name__ == '__main__':
    _, mzml, dump, outpath, spliter, indexer = sys.argv
    main(mzml, dump, outpath, int(spliter), int(indexer))
