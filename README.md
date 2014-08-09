DeMix
=====

### Scripts used in DeMix workflow. 
Sorry for the poorly structured workflow, please feel free to give feedbacks.   



##### Dependent packages:  
numpy  
scipy  
sklearn  
pandas   
lxml   
pymzml (http://pymzml.github.io/)  
pyteomics (http://pythonhosted.org//pyteomics/)  
py-earth (https://github.com/jcrudy/py-earth)      # test only with sklearn on Linux, on other platforms try linear regression. 


##### Procedures:
1. msconvert, RAW to mzML.gz in profile mode, with filter "zeroSample removeExtra 1-2"; http://proteowizard.sourceforge.net/index.shtml    
2. run the TOPPAS pipeline for peak picking and feature detection; http://open-ms.sourceforge.net/downloads/    
3. msconvert, filtering and deisotoping MS/MS spectra, with filters "msLevel 2" and "MS2Deisotope true 0.005Da";   
4. Morpheus search with filtered MS/MS, first-pass database search;   
5. run Python script for pre-processing: Feature list,  First-pass mzML, First-pass PSMs.tsv, Isolation width, Number of threads, resulted in several MGF files;     
6. run msconvert to merge and convert MGF into new deconvoluted mzML;   
7. Morpheus search with deconvoluted MS/MS, second-pass database search;    
8. run Python scripts for post-processing   
...


##### Reference
Zhang, B., Pirmoradian, M., Chernobrovkin, A., & Zubarev, R. a. (2014). DeMix Workflow for Efficient Identification of Co-fragmented Peptides in High Resolution Data-dependent Tandem Mass Spectrometry. Molecular & Cellular Proteomics : MCP. doi:10.1074/mcp.O114.038877      
http://www.ncbi.nlm.nih.gov/pubmed/25100859



