import sys, urllib, subprocess, tempfile, argparse
apars = argparse.ArgumentParser()
apars.add_argument('mzml')
apars.add_argument('-exe', default=r'"ExecutePipeline.exe"')
apars.add_argument('-topp', default=r'TOPP_Processing.toppas')
apars.add_argument('-out_dir', default='.')
apars.add_argument('-trf', default=tempfile.mktemp('.trf'))
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
cmd =  args.exe + ' -in ' + args.topp + ' -resource_file ' + args.trf + ' -out_dir ' + args.out_dir 
subprocess.call(cmd)