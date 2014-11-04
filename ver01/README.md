DeMix
=====

workflow for maximizing peptide identification 

##### Dependent packages:  

Python 2.7  
numpy  
pandas   
lxml   
pymzml http://pymzml.github.io/  
pyteomics http://pythonhosted.org//pyteomics/   
msconvert (ProteoWizard) http://proteowizard.sourceforge.net/index.shtml    
MS-GF+ http://omics.pnl.gov/software/ms-gf   


##### Procedures:
1. msconvert, RAW to mzML.gz in profile mode, with filter "zeroSample removeExtra 1-2"  
2. run_demix_pipeline to execute pipeline under command line, (also execute MS-GF+ database searching)   



##### Reference
Zhang, B., Pirmoradian, M., Chernobrovkin, A., & Zubarev, R. a. (2014). DeMix Workflow for Efficient Identification of Co-fragmented Peptides in High Resolution Data-dependent Tandem Mass Spectrometry. Molecular & Cellular Proteomics : MCP. doi:10.1074/mcp.O114.038877      
http://www.ncbi.nlm.nih.gov/pubmed/25100859



