DeMix: maximizing peptide identification from cofragmentation
=====


I found it would be much easier for general users (normal people who don't work with command line) to go through the whole pipeline under the graphic interface of OpenMS. So I converted my python script into an external tool to integrate in the TOPPAS platform.


##### Dependent packages:  

__Python 2.7__  
__OpenMS 2.0__   
numpy  
pandas  
lxml  
pymzml http://pymzml.github.io/  
pyteomics http://pythonhosted.org//pyteomics/  
msconvert (ProteoWizard) http://proteowizard.sourceforge.net/index.shtml  


MS-GF+ http://omics.pnl.gov/software/ms-gf  
Java runtime environment  


##### Procedures:

1. Copy the __DeMix.ttd__ config file to the OpenMS installation path. (e.g. C:\Program Files\OpenMS-2.0\share\OpenMS\TOOLS\EXTERNAL)   
2. Open the __DeMixTOPP.toppas__ pipeline and change the parameters for the __two__ processes of MSGFAdaptor as well as the wrapper of DeMix, pointing the executable paths of __MSGFPlus.jar__ and the DeMix python script (__feature_ms2_clone_TOPP2.py__), and also the path to the proteome database in __FASTA__ format.  
3. Load __mzML__ spectra files as the input in the pipeline, then execute the pipeline by pressing F5.  
4. Collect results in the TOPP output folders, including FeatureXML files, text exported feature lists, precursor deconvoluted (cloned) MGF spectra, and the database searching resualt (mzID) from MS-GF+.

__Note__:
* Current version works for centroid spectra. If you start with RAW files recorded in profile mode, please picking centroid peaks using the __peak_picking_raw.toppas__ pipeline, or msconvert with its inbuilt peak picking option.


* Please also make sure that Java and Python runtime as well as all dependent packages are installed. Quick check by executing "python feature_ms2_clone_TOPP2.py" under command line.   
* The default parameters are optimized for Thermo Orbitrap Q-Exactive mass spectrometer (__high-resolution__: 70,000 MS1 and 17,500 MS2). Change parameters in TOPP if using data from different instrumental settings.   
* Change the modification file under the path of MSGFPlus if searching for different __PTMs__.  
 * Caution: many bug reports related to the database searching with MS-GF+. If program fails while calling the subprocess of MS-GF+, please check the Java setting in your system environment, and manually execute the command for MS-GF+ generated from the script.


##### Reference
Zhang, B., Pirmoradian, M., Chernobrovkin, A., & Zubarev, R. A. (2014). DeMix Workflow for Efficient Identification of Co-fragmented Peptides in High Resolution Data-dependent Tandem Mass Spectrometry. Molecular & Cellular Proteomics : MCP. doi:10.1074/mcp.O114.038877
http://www.ncbi.nlm.nih.gov/pubmed/25100859
