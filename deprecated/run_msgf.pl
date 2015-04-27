#!perl -wl
use File::Basename;
@ARGV >= 2 or die "$0  proteome.fasta  *.mzML";
$fa = shift; # Proteome database
(undef, $sd, undef) = fileparse($0);
for(@ARGV){
	# each MS/MS spectrum file
    s/\W+$//;
    $cmd = "java -Xmx8g -jar $sd/MSGFPlus/MSGFPlus.jar -mod $sd/MSGFPlus/Mods.txt";
    $cmd .= ' -t 10ppm -ti 0,1 -m 3 -inst 3 -minLength 7 -addFeatures 1 -tda 1 '; # QExactive HCD
    # $cmd .= " -ntt 1 "; # 1 = semi-enzymic ; 0 = non-specific
    $cmd .= " -s $_ -d $fa -o $_.mzid && "; 
    $cmd .= "java -Xmx8g -cp $sd/MSGFPlus/MSGFPlus.jar edu.ucsd.msjava.ui.MzIDToTsv -i $_.mzid"; # convert mzid to table
    print $cmd;
}


__END__
MS-GF+ Beta (v10089) (7/16/2014)
Usage: java -Xmx3500M -jar MSGFPlus.jar
        -s SpectrumFile (*.mzML, *.mzXML, *.mgf, *.ms2, *.pkl or *_dta.txt)
        -d DatabaseFile (*.fasta or *.fa)
        [-o OutputFile (*.mzid)] (Default: [SpectrumFileName].mzid)
        [-t PrecursorMassTolerance] (e.g. 2.5Da, 20ppm or 0.5Da,2.5Da, Default: 20ppm)
           Use comma to set asymmetric values. E.g. "-t 0.5Da,2.5Da" will set 0.5Da to the minus (expMass<theoMass) and 2.5Da to plus (expMass>theoMass)
        [-ti IsotopeErrorRange] (Range of allowed isotope peak errors, Default:0,1)
           Takes into account of the error introduced by chooosing a non-monoisotopic peak for fragmentation.
           The combination of -t and -ti determins the precursor mass tolerance.
           E.g. "-t 20ppm -ti -1,2" tests abs(exp-calc-n*1.00335Da)<20ppm for n=-1, 0, 1, 2.
        [-thread NumThreads] (Number of concurrent threads to be executed, Default: Number of available cores)
        [-tda 0/1] (0: don't search decoy database (Default), 1: search decoy database)
        [-m FragmentMethodID] (0: As written in the spectrum or CID if no info (Default), 1: CID, 2: ETD, 3: HCD)
        [-inst MS2DetectorID] (0: Low-res LCQ/LTQ (Default), 1: Orbitrap/FTICR, 2: TOF, 3: Q-Exactive)
        [-e EnzymeID] (0: unspecific cleavage, 1: Trypsin (Default), 2: Chymotrypsin, 3: Lys-C, 4: Lys-N, 5: glutamyl endopeptidase, 6: Arg-C, 7: Asp-N, 8: alphaLP, 9: no cleavage)
        [-protocol ProtocolID] (0: Automatic (Default), 1: Phosphorylation, 2: iTRAQ, 3: iTRAQPhospho, 4: TMT, 5: Standard)
        [-ntt 0/1/2] (Number of Tolerable Termini, Default: 2)
           E.g. For trypsin, 0: non-tryptic, 1: semi-tryptic, 2: fully-tryptic peptides only.
        [-mod ModificationFileName] (Modification file, Default: standard amino acids with fixed C+57)
        [-minLength MinPepLength] (Minimum peptide length to consider, Default: 6)
        [-maxLength MaxPepLength] (Maximum peptide length to consider, Default: 40)
        [-minCharge MinCharge] (Minimum precursor charge to consider if charges are not specified in the spectrum file, Default: 2)
        [-maxCharge MaxCharge] (Maximum precursor charge to consider if charges are not specified in the spectrum file, Default: 3)
        [-n NumMatchesPerSpec] (Number of matches per spectrum to be reported, Default: 1)
        [-addFeatures 0/1] (0: output basic scores only (Default), 1: output additional features)
Example (high-precision): java -Xmx3500M -jar MSGFPlus.jar -s test.mzXML -d IPI_human_3.79.fasta -t 20ppm -ti -1,2 -ntt 2 -tda 1 -o testMSGFPlus.mzid
Example (low-precision): java -Xmx3500M -jar MSGFPlus.jar -s test.mzXML -d IPI_human_3.79.fasta -t 0.5Da,2.5Da -ntt 2 -tda 1 -o testMSGFPlus.mzid
