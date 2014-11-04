# bo.zhang@ki.se
# A simplified version of DeMix data processing workflow.

import sys
import urllib
import subprocess
import tempfile
import argparse
import os


apars = argparse.ArgumentParser()
apars.add_argument('mzml')
apars.add_argument('-exe', default='ExecutePipeline.exe')
apars.add_argument('-topp', default=os.path.join(os.path.dirname(sys.argv[0]), 'TOPP_Processing.toppas'))
apars.add_argument('-db', default='HUMAN.fa')
apars.add_argument('-out_dir', default='.')
apars.add_argument('-trf', default=tempfile.mktemp('.trf'))
apars.add_argument('-w', default=4.0)

args = apars.parse_args()

trf = '''<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.6.2" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_6_2.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="1" description="">
    <ITEMLIST name="url_list" type="string" description="" required="false" advanced="false">
      <LISTITEM value="file:%s"/>
    </ITEMLIST>
  </NODE>
</PARAMETERS>
''' % urllib.pathname2url(args.mzml)
open(args.trf, 'w').write(trf)

# '======= run TOPP workflow for peak picking and feature detection'
cmd = args.exe  + ' -in ' + args.topp \
				+ ' -resource_file ' + args.trf \
				+ ' -out_dir ' + args.out_dir
print cmd
subprocess.call(cmd)


# '======= first pass MS-GF+ database searching '
centroidSpec = os.path.join(args.out_dir,  'TOPPAS_out', '004-PeakPickerHiRes', os.path.basename(args.mzml).replace('.gz', ''))
cmd = 'java -Xmx8g -jar ' + os.path.join(os.path.dirname(args.topp), 'MSGFPlus', 'MSGFPlus.jar')

# change PTMs in the Mods.txt file under MSGFPlus folder.
cmd += ' -mod ' + os.path.join(os.path.dirname(args.topp), 'MSGFPlus', 'Mods.txt') \
 	+ ' -d ' + args.db \
	+ ' -s ' + centroidSpec \
	+ ' -o ' + centroidSpec + '.mzid'

# Q-Exactive, HCD, trypsin, 2 miscleavage, 0/1 13C, 10 ppm precursor tol.
cmd += ' -t 10ppm -ti 0,1 -m 3 -inst 3 -minLength 7 -addFeatures 1 -tda 1 '
print cmd
subprocess.call(cmd)


# '======== convert mzid to tsv '
cmd = 'java -Xmx8g -cp ' \
		+ os.path.join(os.path.dirname(args.topp), 'MSGFPlus', 'MSGFPlus.jar') \
		+ ' edu.ucsd.msjava.ui.MzIDToTsv -i ' \
		+ centroidSpec + '.mzid'
print cmd
subprocess.call(cmd)


# '======== DeMix '
import feature_ms2_clone
psm = feature_ms2_clone.load_PSM(centroidSpec + '.tsv')
t = psm['PrecursorError(ppm)'].std() * 3
t = t > 10 and 10 or t

featureTab = os.path.join(args.out_dir,  'TOPPAS_out', '009-TextExporter',
                          os.path.basename(args.mzml).replace('.gz', '').replace('.mzML', '.csv'))
demixSpec = feature_ms2_clone.spectra_clone(
    featureTab, centroidSpec, psm, float(args.w))


# '======== second pass MS-GF+ dababase search '
cmd = 'java -Xmx8g -jar ' + os.path.join(os.path.dirname(args.topp), 'MSGFPlus', 'MSGFPlus.jar') \
	+ ' -mod ' + os.path.join(os.path.dirname(args.topp), 'MSGFPlus', 'Mods.txt') \
	+ ' -d ' + args.db \
	+ ' -s ' + demixSpec \
	+ ' -o ' + demixSpec + '.mzid'

cmd += ' -ti 0,1 -m 3 -inst 3 -minLength 7 -maxLength 50 -addFeatures 1 -tda 1 '
cmd += ' -t %.1fppm ' % t
print cmd
subprocess.call(cmd)
