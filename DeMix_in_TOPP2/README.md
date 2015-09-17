Calling DeMix inside TOPP
=====

1. Copy the DeMix.ttd config file to the OpenMS installation path. e.g. C:\Program Files\OpenMS-2.0\share\OpenMS\TOOLS\EXTERNAL  
2. Open the .toppas workflow and change the parameters for the two processes of MSGFAdaptor as well as the wrapper of DeMix, pointing the executable paths of MSGFPlus.jar and the DeMix python script (feature_ms2_clone_TOPP2.py), and also the path to the proteome database in FASTA format.  
3. Load mzML spectra files as the input in the pipeline, then execute the pipeline by pressing F5.  

Note: For centroided spectra, remove the PeakPickerHiRes and directly link mzML input to down-stream processes. Also make sure that Java and Python runtime as well as all dependent packages are installed. Quick check by executing "python feature_ms2_clone_TOPP2.py" under command line.
