import sys
import os
import csv
import numpy
import pymzml
import xml
import gzip
from pyteomics import mzid


def load_feature_table(fn):
    table = []
    with open(fn, 'r') as fh:
        rd = csv.reader(fh, delimiter=',')
        for row in rd:
            if row[0] == 'FEATURE':
                _, rt, mz, _, chg, _, _, _, _, rtl, rtr = row
                table.append([float(mz), int(chg), float(rtl), float(rtr), float(rt)])
    table.sort(key=lambda x: x[3])
    return table


def load_mzid(fn, qval=0.01):
    from pprint import pprint
    psms = []
    specids = [0]
    psmReader = mzid.read(fn)
    for psm in psmReader:
        if psm.has_key('SpectrumIdentificationItem'):
            try:
                specids.append( int(psm['scan number(s)']))
            except KeyError:
                specids.append( int( psm['spectrumID'].split('=')[-1] ))
            else:
                pass

            for match in psm['SpectrumIdentificationItem']:
                if match['MS-GF:QValue'] < qval and match['rank'] == 1 and match['IsotopeError'] == 0 and 2 <= match['chargeState'] <= 4:
                    dm = match['experimentalMassToCharge'] - match['calculatedMassToCharge']
                    dm = dm * 1e6 / match['calculatedMassToCharge']
                    psms.append(dm)
    return numpy.array(psms), max(specids)


def spectra_clone(feature_fn, mzml_fn, dm_offset, max_scan=0, full_iso_width=4.0, out_dir=None, MS1_Precision = 1e-5):
    features = load_feature_table(feature_fn)
    iso_width = full_iso_width / 2.0
    sys.stderr.write("Auto correct precursor m/z offset: %.2f ppm \n" % dm_offset)
    ns = {'ns0':"http://psi.hupo.org/ms/mzml"}
    
    if mzml_fn.endswith('.gz'):
        fh = gzip.open(mzml_fn)
    else:
        fh = open(mzml_fn)
    

    if out_dir == None:
        out_dir = os.path.dirname(mzml_fn)

    outpath = os.path.join(out_dir, os.path.basename(mzml_fn) + ".demix.mgf" )
    sys.stdout = open(outpath, 'wb')

    speciter = pymzml.run.Reader(mzml_fn)
    timescale = 0
    iso_left, iso_right = (0, 0)
    features.sort(key=lambda x: x[0])
    fmz_all = numpy.array([f[0] for f in features])
    try:
        for spec in speciter:
            element = spec.xmlTree.next()
            title = element.get('id')
            idx = int(title.split('scan=')[-1])
            if idx % 1000 == 0 and max_scan > 0:
                sys.stderr.write("DeMix %d MS/MS (~%.1f%%)\n" % (idx, idx * 100.0 / max_scan))

            if not timescale:
                xmltext = xml.etree.ElementTree.tostring(element)
                if xmltext.count(r'unitName="second"'):
                    timescale = 1
                else:
                    timescale = 60

            if spec['ms level'] == 2.0:
                try:
                    rt = float(spec['scan time']) * timescale
                except:
                    continue

                pmz = None
                if iso_left == 0:
                    iso_left = iso_width
                    iso_right = iso_width

                    try:
                        # automatically adjust isolation window width
                        c = filter(lambda c: 'precursor' in c.tag, element.getchildren())[0]
                        c = filter(lambda c: 'precursor' in c.tag, c.getchildren())[0]
                        c = filter(lambda c: 'isolation' in c.tag, c.getchildren())[0]
                        pmz, iso_left, iso_right = [float(c.get('value')) for c in c.findall('ns0:cvParam', ns)]
                    except:
                        pass

                for p in spec['precursors']:
                    if pmz == None:
                        pmz = float(p['mz'])
                    try:
                        pz = int(p['charge'])
                    except:
                        pz = 0

                    featured = False
                    peaks = sorted(filter(lambda x: x[1], spec.centroidedPeaks), key=lambda i: i[0])

                    l_idx = fmz_all.searchsorted(pmz - iso_left, side='left')
                    r_idx = fmz_all.searchsorted(pmz + iso_right, side='right')
                    for f in features[l_idx:r_idx+1]:
                        fmz, fz, frt_left, frt_right, frt = f
                        if frt_left < rt < frt_right:
                            if abs(pmz - fmz) / pmz <= MS1_Precision: 
                                featured = True
                            print 'BEGIN IONS'
                            print 'TITLE=%d[%d:%f:%f]' % (idx, features.index(f), fmz, frt)
                            print 'RTINSECONDS=%f' % rt
                            print 'PEPMASS=%f' % (fmz - fmz * dm_offset * 1e-6)
                            print 'CHARGE=%d+' % fz
                            print 'RAWFILE=%s [%f:%d] diff:%f' % (title, pmz, pz, (fmz - pmz))
                            for a, b in peaks:
                                print a, b
                            print 'END IONS\n'

                    if featured == False and pz > 1:
                        print 'BEGIN IONS'
                        print 'TITLE=%d[-:%f:%f]' % (idx, pmz, rt)
                        print 'RTINSECONDS=%f' % rt
                        print 'PEPMASS=%f' % (pmz - pmz * dm_offset * 1e-6)
                        print 'CHARGE=%d+' % pz
                        print 'RAWFILE=%s' % (title)
                        for a, b in peaks:
                            print a, b
                        print 'END IONS\n'
    except (KeyError, ValueError):
        pass    
    return outpath


if __name__ == '__main__':
    import argparse
    sys.stderr.write(' '.join(sys.argv))

    apars = argparse.ArgumentParser()

    apars.add_argument('mzml')      # centroided MS/MS spectra in mzML, the same file which has been used in the first-pass database search.
    apars.add_argument('-feature')  # feature csv table exported from FeatureXML by TOPP. 
    apars.add_argument('-psm')      # first-pass database search result (MS-GF+ output mzid format)
    apars.add_argument('-w', default=4.0) # the total width of precursor isolation window when failed to detect the actual window size in mzML. 
    apars.add_argument('-out_dir', default='.')

    args = apars.parse_args()

    macc, max_scan = load_mzid(args.psm)
    sys.stderr.write("\nMean precursor mass error (ppm): %.3f SD: %.3f\n" % (macc.mean(), macc.std()))
    spectra_clone(feature_fn = args.feature, 
        mzml_fn = args.mzml, 
        dm_offset = macc.mean(), 
        max_scan = max_scan, 
        full_iso_width = float(args.w), 
        out_dir = args.out_dir)

