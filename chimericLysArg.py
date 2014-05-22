# bo.zhang@ki.se
# Chimeric MS/MS estimation based on co-existence of protonated Lys and Arg.

import pymzml, sys


speciter = pymzml.run.Reader(sys.argv[1])

tol = 1e-5
l = 1.0 - tol
r = 1.0 + tol

lys = 147.11280
arg = 175.11895

msms = []
try:
    for spec in speciter:
        if spec['ms level'] == 2.0:
        	lysPlus = filter(lambda x: (lys*l< x[0] < lys*r), spec.peaks)
        	argPlus = filter(lambda x: (arg*l< x[0] < arg*r), spec.peaks)
        	msms.append((bool(lysPlus), bool(argPlus)))
except KeyError:
    pass

tot = msms.__len__()
chi = msms.count((True, False)) + msms.count((False, True))
one = msms.count((True, True))
non = msms.count((False, False))

print tot, chi, one, non
print chi * 100.0 / tot
print one * 100.0 / tot