# Land Carbon Budget: Intact and Non-Intact Forest NBP from TRENDY-v11

***********************************************************************
 Step (1) Create an auxiliary file "IntactAndNonIntactForest_0.5deg.nc"
***********************************************************************
The following steps are done in Google Earth Engine (GEE) platform:

  1) Convert Hansen tree cover (30m spatial resolution) to forest cover. 
     To do this, FAO definition of forest (more that 20% tree cover and a minimum continuity of 0.5 ha) is used.
  2) Intact and Non-Intact "Forest" masks came from Popatov except over Canada and Brazil from where we got more acurate masks.
       ==> Popatov mask was updated over Brazil and Canada
  3) Merge the two datasets to get the Intact and Non-Intact forest area per gridcells of around 30m spatial resolution.
  4) Redrid the data to 0.5 degree spatial resolution. 
     Because of the computational issue, this has been done in two steps. From 30m to 0.01 degree, then from 0.01 to 0.5 degree.
  5) The 0.5 degree Intact and Non-Intact forest area is saved in "IntactAndNonIntactForest_0.5deg.nc" NetCDF file.
     The javascript code "IntactAndNonIntactForest_0.5deg.js" that is used to generate this file is available here. 

This last step is done outside GEE

  6) We compute the ratio between observed forest cover and the median forest cover coming from the 10 TRENDY S2 models that provide 
     landCoverFrac. Models are:'CLASSIC','YIBs','CABLE-POP','JSBACH', 'ISBA-CTRIP','LPX-Bern','OCN','JULES','VISIT','VISIT-NIES','SDGVM'.
     This ratio is included in the "IntactAndNonIntactForest_0.5deg.nc" NetCDF file and used in the Step (5).

The NetCDF is availble via request to ram.alkama[at]hotmail.fr

    
**************************************************************************
Step (2) select dates and do annual mean
***************************************************************************
 For all models we
  1) extract nbppft, nbp and landCover files (if available) over 1990-2021 
  2) do annual mean 

**************************************************************************
Step (3) Intact and Non Intact forest NBP from models that provide nbppft.
 - The models are: 'CLASSIC','YIBs','CABLE-POP','JSBACH', 'ISBA-CTRIP'
 - ISBA-CTRIP is not yet uploaded in the server but the method is included here
***************************************************************************

  1) From landCoverFrac and nbppft we computed mean forest nbp (kg/m2/s)for each gridcell.
     -  ForestNBP= Sum(ForestPFTfrac * Forestnbppft)/sum(ForestPFTfrac) 

  2) Compute mean forest nbp for ISBA-CTRIP model.
     -  nbpTree=nppTree-rhTree-DisturbancesTree
     - where:   DisturbancesTree=fCleach+fFire
     - We assume most of fFire and fCleach originates from forest, if forest exists in the gridcell.
     - we then do same as 1) above.

  3) If low spatial resolution regrid into 0.5x0.5 deg

  4) Since the unit of forest NBP is kg/m2/s we multiply it by Intact and NonIntact forest area
     that came from the netcdf file described in "step (1)" and number of seconds in the year to get "kg/gridcell/yr"
 
*********************************************************************************
Step (4) Intact and Non Intact forest NBP from models that did not provide nbppft
         but provide landCoverFrac.
 - The models are: 'LPX-Bern','OCN','JULES','VISIT','VISIT-NIES','SDGVM'
*********************************************************************************
  1) If low spatial resolution regrid into 0.5x0.5 deg

  2) for each model and gridcell, we compute the ratio between observed and TRENDY-v11 S2 forest cover

  3) multiply simulated nbp by this ratio, land area and number of seconds in the year
    ==> from kg/m2/s to kg/gridcell/yr

  4) Split into Intact and Non-Intact forest NBP using "IntactAndNonIntactForest_0.5deg.nc" 
     "see step (1)"
  

*********************************************************************************************************
Step (5) Intact and Non Intact forest NBP from models that neither provide nbppft nor landCoverFrac.
 - The models are: 'IBIS','CLM5.0','ORCHIDEE','ISAM','DLEM','LPJ-GUESS'

NB: LPJ-GUESS provide landCoverFrac but because of the specificity of this model we used it in this step
**********************************************************************************************************
  1) If low spatial resolution regrid into 0.5x0.5 deg

  2) We use the ratio between observed forest cover and median of the 10 TRENDY S2 models. This ratio is stored in
     "IntactAndNonIntactForest_0.5deg.nc" NetCDF file. See Step (1.6).

  3) multiply simulated nbp by this ratio, land area and number of seconds in the year
    ==> from kg/m2/s to kg/gridcell/yr

  4) Split into Intact and Non-Intact forest NBP using "IntactAndNonIntactForest_0.5deg.nc" 
     "see step (1)"



Contact: ram.alkama@hotmail.fr
last update: 09/09/2022
