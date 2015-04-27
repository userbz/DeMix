# bo.zhang@ki.se
# Morpheus AS rescoring

import sys
import csv
import numpy
import pandas
from scipy.stats import norm

csvout = csv.writer(sys.stdout, delimiter='\t')


def _calc_parameters(df, decoy=False, tol_ms2=20):
    # use only high quality PSMs (original FDR < 5%)
    dx = df[(df["Q-Value (%)"] < 5) & (df['Decoy?'] == decoy)] 
    
    # fit normal distribution with log-transformed values of intensity fraction
    frac_log_fit = norm.fit(numpy.log(dx['Fraction of Intensity Matching'])) 
    
    
    # fit normal distribution with precursor mass errors
    ms1ppm_fit = norm.fit(dx['Precursor m/z Error (ppm)'])
    
    # fit with fragment mass errors in a limit range. 
    dmsmsppm = []
    for arr in dx['Nearest Matches (ppm)'].values:
        matching = filter(lambda p: -tol_ms2 < p < tol_ms2, arr)
        dmsmsppm += matching
    ms2ppm_fit = norm.fit(dmsmsppm)
    return frac_log_fit, ms1ppm_fit, ms2ppm_fit


def rescore(df, tol_ms1=10, tol_ms2=20):
    df = df[(df['Precursor m/z Error (ppm)'] < tol_ms1) & (df['Precursor m/z Error (ppm)'] > -tol_ms1)]
    ppmArray = []
    for i, x in df.iterrows():
        t = eval(x['Theoretical Products'])
        m = eval(x['Nearest Matches'])
        p = [ (e[0] - e[1]) * 1e6 / e[1] for e in zip(m, t)]
        ppmArray.append(p)

    df['Nearest Matches (ppm)'] = ppmArray

    target_fits = _calc_parameters(df, decoy=False, tol_ms2=tol_ms2)
    decoy_fits  = _calc_parameters(df, decoy=True, tol_ms2=tol_ms2)
    
    # print target_fits
    # print decoy_fits

    target_frac_mean, target_frac_std = target_fits[0]
    target_ms1_mean, target_ms1_std = target_fits[1]
    target_ms2_mean, target_ms2_std = target_fits[2]

    decoy_frac_mean, decoy_frac_std = decoy_fits[0]

    ms2_L_limit = target_ms2_mean - target_ms2_std * 2
    ms2_R_limit = target_ms2_mean + target_ms2_std * 2

    sys.stderr.write("MS1_SD:%.3f  MS2_SD:%.3f\n" % (target_ms1_std, target_ms2_std) )

    csvout.writerow(df.columns)
    for i, x in df.iterrows():
        # sub score S1: p-value of precursor mass error
        ms1Score = 2 * norm.sf(abs(x['Precursor m/z Error (ppm)'] - target_ms1_mean) / target_ms1_std)
        
        # sub score S2: counts of matched fragment peaks and complementary pairs.
        matching = map(lambda p: ms2_L_limit < p < ms2_R_limit, x['Nearest Matches (ppm)'])
        matchingScore = matching.count(True)
        for b in xrange(len(matching)):
            if b % 2 == 0 and matching[b] and matching[b+1]:
                matchingScore += 1


        # sub score S3: probability ratio of ion intensity fraction
        frac = x['Fraction of Intensity Matching']
        fracScore = frac # use the value from original Morpheus result
        
        frac = numpy.log(frac)
        frac_pdf_decoy = norm.pdf((frac - decoy_frac_mean)/decoy_frac_std)
        frac_pdf_target = norm.pdf((frac - target_frac_mean)/target_frac_std)
        fracScore = (frac_pdf_target - frac_pdf_decoy) / (frac_pdf_target + frac_pdf_decoy)
        
        # print i, matchingScore, ms1Score, fracScore

        # final PSM score
        if ms1Score >= 0.0001:
            x['Morpheus Score'] = matchingScore + fracScore + ms1Score
        else:
            x['Morpheus Score'] = 0

        csvout.writerow(x.values)


if __name__ == '__main__':
    df = pandas.read_table(sys.argv[1])
    df = rescore(df, 10, 20)
