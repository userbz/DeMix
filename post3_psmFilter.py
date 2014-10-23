# bo.zhang@ki.se
# PSM list trimmer for Morpheus-AS rescored result

import sys
import csv


def load_psm(fh, baselen=7):
    ''' load MorpheusAS PSM table '''
    psm = []
    rd = csv.reader(fh, delimiter='\t')
    hd = rd.next()
    for row in rd:
        if int(row[hd.index('Missed Cleavages')]) > 3:
            continue
        if len(row[hd.index('Base Peptide Sequence')]) >= baselen:
            psm.append(row)
    psm.sort(key=lambda x: float(x[hd.index('Morpheus Score')]), reverse=True)
    return hd, psm


def psm_dedup(psm, titIx, seqIx, scoIx):
    ''' remove duplications in the PSM list:
        one feature gives only one peptide ID, 
        one deconvoluted spectrum belongs to only one feature, and appears only once.
    '''
    titleSet = {}
    for row in psm:
        scan_title, feature_title = row[titIx].split('[') # spectral index text processing
        seq = row[seqIx]
        if titleSet.has_key(feature_title) and titleSet[feature_title] != seq:
            row[scoIx] = 0    # drop low-score IDs of same feature
        else:
            titleSet[feature_title] = seq

        if titleSet.has_key(scan_title):
            if seq in titleSet[scan_title]:
                row[scoIx] = 0  # drop duplicated ID for the same spectrum
            else:
                titleSet[scan_title].add(seq)
        else:
            titleSet[scan_title] = set([seq])
    psm.sort(key=lambda x: float(x[scoIx]), reverse=True)


# Define PSM filters
def psm_filter(psm, tarIx, flt, FDR=1.0):
    '''trimming PSM list by FDR'''
    t, d, fdr = (0, 0, 0)
    newpsm = []
    for row in psm:
        newpsm.append(row)
        if flt(row) == True:
            if fdr >= FDR:
                newpsm.pop() # remove this PSM from resultant list for high FDR
                continue

            if row[tarIx] == 'True':
                t += 1
            else:
                d += 1

            # FDR difinition: Decoys / Targets
            fdr = d * 100.0 / t  

    return newpsm


def unipep_fdr(psm, seqIx, scoIx, tarIx, FDR=1.0):
    '''FDR trimming at the unique peptide sequence level'''
    unipeptides = {}
    for row in psm:
        uniseq = row[seqIx]
        target = bool(row[tarIx] == 'True')
        score = float(row[scoIx])
        if not target:
            score *= -1
        
        if unipeptides.has_key(uniseq):
            # unipeptides[uniseq] = abs(unipeptides[uniseq]) >  abs(score) and unipeptides[uniseq] or score
            unipeptides[uniseq] += score
        else:
            unipeptides[uniseq] = score

    peplist = sorted(unipeptides.items(), key=lambda x: abs(x[1]), reverse=True)
    
    candidates = set([])
    t, d = (0, 0)
    for x in peplist:
        if x[1] < 0:
            d += 1
        else:
            t += 1
        fdr = d * 100.0 / t

        if fdr < FDR:
            candidates.add(x[0])
        else:
            psm = filter(lambda x: x[seqIx] in candidates, psm)
            break
    return psm

if __name__ == '__main__':
    with open(sys.argv[1]) as fh:
        hd, psm = load_psm(fh, baselen=7)
    
    # FDR = float(sys.argv[2])
    FDR = 1.0
    
    seqIx = hd.index('Base Peptide Sequence')
    pepIx = hd.index('Peptide Sequence')
    chgIx = hd.index('Precursor Charge')
    scoIx = hd.index('Morpheus Score')
    titIx = hd.index('Spectrum Title')     
    tarIx = hd.index('Target?')

    psm_dedup(psm, titIx, pepIx, scoIx) 

    # hierarchical filtration
    filterfuncs = []

    # high-risk: RK-P cleavage
    filterfuncs.append(lambda x: x[seqIx].startswith('P'))
    
    # mid-risk: basic residues >= charges
    filterfuncs.append(lambda x: (x[seqIx].count('H') + x[seqIx].count('K') + x[seqIx].count('R')) > float(x[chgIx]))
    filterfuncs.append(lambda x: (x[seqIx].count('H') + x[seqIx].count('K') + x[seqIx].count('R')) == float(x[chgIx]))
    
    # all PSMs    
    filterfuncs.append(lambda x: True)

    for f in filterfuncs:
        psm = psm_filter(psm, tarIx, flt=f, FDR=FDR)

    psm = unipep_fdr(psm, pepIx, scoIx, tarIx, FDR=FDR)




    # FDR fitered results
    t, d = (0,0)
    tSet = set()
    dSet = set()

    csvout = csv.writer(sys.stdout, delimiter="\t")
    csvout.writerow(hd)
    for row in psm:
        csvout.writerow(row)
        uniseq = row[seqIx]
        if row[tarIx] == 'True':
            t += 1
            tSet.add(uniseq)
        else:
            d += 1
            dSet.add(uniseq)

    csvout = csv.writer(sys.stderr, delimiter="\t")
    tl = len(tSet)
    dl = len(dSet)
    csvout.writerow([tl+dl, tl, dl, dl*1.0/(tl+dl), len(psm), psm.pop()[scoIx]])
