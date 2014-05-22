# Bo.Zhang@ki.se
# extending PSM list from second-pass Morpheus search for rescoring


import sys
import pymzml
import numpy
import pandas


def nearest(target, arr):
    try:
        return arr[numpy.abs(arr - target).argmin()]
    except:
        return 0

def peak_pair(target, arr):
    match = [nearest(p, arr) for p in target]
    return repr(match)


def pymzml_psm(fn, df):
    speciter = pymzml.run.Reader(fn)
    index_set = set(df.index)
    df['Nearest Matches'] = ['' for _ in df.index]
    try:
        for spec in speciter:
            idx = int(spec.xmlTree.next().get('index')) + 1
            if idx and idx % 2000 == 0:
                sys.stderr.write("%d  %s\n" % (idx, fn))
            if spec['ms level'] != 2 or idx not in index_set:
                continue
            theoSpec = df.loc[idx]['Theoretical Products']
            specPeaks = numpy.array(map(lambda p: p[0], spec.peaks))
            match = peak_pair(theoSpec, specPeaks)
            df.loc[idx, 'Nearest Matches'] = match
    except KeyError:
        pass

    return df


if __name__ == '__main__':
    df = pandas.read_table(sys.argv[1], index_col= 1)
    if 'Theoretical Products' in df.columns:
        df['Theoretical Products'] = [eval(i) for i in df['Theoretical Products']]
    else:
        import psmTheoretical
        df = psmTheoretical.add_theoretical(sys.argv[1])
        df.to_csv(sys.argv[1]+ '.ext', index=0, sep='\t')
    df = pymzml_psm(sys.argv[2], df)
    df.to_csv(sys.argv[1]+ '.ext.matched', index=0, sep='\t')


