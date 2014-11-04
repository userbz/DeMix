# Bo.Zhang@ki.se
# DO NOT RUN IT DIRECTLY
# peptide theoretical mass calculation for Morpheus PSM list
# predefined masses for modifications: 'Ac-', 'oxM', 'cmC', 'daN', 'daQ'


import sys
import csv
import pandas
from pyteomics import mass, parser

csvout = csv.writer(sys.stdout, delimiter='\t')

composition = mass.std_aa_comp
composition['cmC'] = mass.std_aa_comp['C'].copy()
composition['cmC']['C'] += 2
composition['cmC']['H'] += 3
composition['cmC']['N'] += 1
composition['cmC']['O'] += 1

composition['Ac-'] = composition['H-'].copy()
composition['Ac-']['C'] += 2
composition['Ac-']['H'] += 2
composition['Ac-']['O'] += 1

composition['oxM'] = composition['M'].copy()
composition['oxM']['O'] += 1

composition['daN'] = composition['N'].copy()
composition['daN']['H'] -= 1
composition['daN']['N'] -= 1
composition['daN']['O'] += 1

composition['daQ'] = composition['Q'].copy()
composition['daQ']['H'] -= 1
composition['daQ']['N'] -= 1
composition['daQ']['O'] += 1

modLabels = parser.std_labels + ['Ac-', 'oxM', 'cmC', 'daN', 'daQ']


def seqModX(seq):
    seq = seq.split('.')[1]
    seq = seq.replace('(acetylation of protein N-terminus)', 'Ac-')
    seq = seq.replace('M(oxidation of M)', 'oxM')
    seq = seq.replace('C[carbamidomethylation of C]', 'cmC')
    seq = seq.replace('N(deamidation of N)', 'daN')
    seq = seq.replace('Q(deamidation of Q)', 'daQ')
    return seq


def calc_precursor_theoretical(seq, z):
    try:
        parseq = parser.parse(seqModX(seq), labels=modLabels, show_unmodified_termini=True)
        theomass = mass.calculate_mass(parsed_sequence=parseq, aa_comp=composition)
        theomz = mass.calculate_mass(parsed_sequence=parseq, aa_comp=composition, charge=z)
        return (parseq, theomass, theomz)
    except :
        return (None, None, None)
    


def in_silico_fragmentation(fn):
    df = pandas.read_table(fn)
    products = {}
    for i, x in df.iterrows():
        xchg = x['Precursor Charge']
        bseq = x['Base Peptide Sequence']
        seq = x['Peptide Sequence']
        if not products.has_key(seq):
            parseq, theomass, theomz = calc_precursor_theoretical(seq, int(xchg))
            if parseq == None:
                products[seq] = [0.0, 0.0]
                continue

            theoSpec = []
            # for c in xrange(1, int(xchg/2)+1):
            for c in [1]:
                for n in xrange(1, len(bseq)):
                    bproduct = parseq[:n + 1] + [parseq[-1]]
                    yproduct = ['H-'] + parseq[n + 1:]

                    bp = mass.calculate_mass(parsed_sequence=bproduct, ion_type='b', aa_comp=composition, charge=c)
                    yp = mass.calculate_mass(parsed_sequence=yproduct, ion_type='y', aa_comp=composition, charge=c)
                    theoSpec.append(bp)
                    theoSpec.append(yp)

                    # print "b:%d:%f" % (n,bp), bproduct
                    # print "y:%d:%f" % (len(bseq)-n,yp), yproduct

            products[seq] = theoSpec
    return products


def add_theoretical(fn):
    df = pandas.read_table(fn)
    df = df[df['Matching Products'] > 2]

    theoretical_mz = map(lambda x: calc_precursor_theoretical(x[1]['Peptide Sequence'], int(x[1]['Precursor Charge']))[2], df.iterrows())
    df['Theoretical m/z'] = theoretical_mz
    df['Precursor m/z Error (ppm)'] = (df['Precursor m/z'] - df['Theoretical m/z']) * 1e6 / df['Theoretical m/z']
    
    products = in_silico_fragmentation(fn)
    df['Theoretical Products'] = map(lambda n: products[n], df['Peptide Sequence'])
    df.index = df['Spectrum Number'].values
    return df


if __name__ == '__main__':
    df = add_theoretical(sys.argv[1])
    df.to_csv(sys.argv[2], sep='\t', index=0)
