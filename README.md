# Land Carbon Budget: Intact and Non-Intact Forest NBP from TRENDY-v11 S2 simulations

***********************************************************************
 Step (1) Create an auxiliary file "IntactAndNonIntactForest_0.5deg.nc"
***********************************************************************
The following steps are done in Google Earth Engine (GEE) platform:

  1) Convert Hansen tree cover (30m spatial resolution) to forest cover. 
     To do this, FAO definition of forest (more than 20% tree cover per gridcell and a minimum continuity of 0.5 ha) is used.
  2) Intact and Non-Intact "Forest" masks came from Potapov et al. (2017) except over Canada and Brazil, two countries
with large areas of unmanaged forest, this study uses the national gridded map used in the respective National GreenHouse Gas Inventories (Canada, 2021; Brazil, 2020).
       ==> Popatov mask was updated over Brazil and Canada
  3) Merge the two datasets to get the Intact and Non-Intact forest area per gridcells of around 30m spatial resolution.
  4) Redrid the data to 0.5 degree spatial resolution (sum the area of all forest gridcells present inside the 0.5 degree). 
     Because of the computational issue, this has been done in two steps. From 30m to 0.01 degree, then from 0.01 to 0.5 degree.
  5) The 0.5 degree Intact and Non-Intact forest area is saved in "IntactAndNonIntactForest_0.5deg.nc" NetCDF file.
     The javascript code "IntactAndNonIntactForest_0.5deg.js" that is used to generate this file is available here. 

This last step is done outside GEE

  6) We compute the ratio between observed forest cover and the median forest cover coming from the 10 TRENDY S2 models 
     that provide information on land cover fraction per plant functional type (variable/file: landCoverFrac). Models are:'CLASSIC','YIBs','CABLE-POP','JSBACH', 'LPX-Bern','OCN','JULES','VISIT','VISIT-NIES','SDGVM'.
     This ratio is included in the "IntactAndNonIntactForest_0.5deg.nc" NetCDF file and used in the Step (5).


Forest pfts are:
{'ORCHIDEE':[1,2,3,4,5,6,7,8],'JSBACH':[2,3,4,5],'CLASS-CTEM':[0,1,2,3,4],'DLEM':[4,5,6,7,8,9,10,11],
  'OCN':[1,2,3,4,5,6,7,8],'CABLE-POP':[0,1,2,3],'ISAM':[0,1,2,3,4,13,14,15,16,17,19,23],
   'SDGVM':[6,7,8,9],'JULES':[0,1,2,3,4],'CLASSIC':[0,1,2,3,4],
           'VISIT':[0,1,2,3,4,5,6,7],'YIBs':[0,1,2],'LPX-Bern':[0,1,2,3,4,5,6,7],'CLM5.0':[1,2,3,4,5,6,7,8],'LPJ':[0,1,2,3,4,5]} 


The NetCDF is availble via request to ram.alkama[at]hotmail.fr

Reference

Potapov et al. The last frontiers of wilderness: Tracking loss of intact forest landscapes from 2000 to 2013. https://www.science.org/doi/10.1126/sciadv.1600821, 2017.

Brazil: National Communication 3, https://unfccc.int/documents/66129 , 2020.

Canada. National Inventory Report (NIR), https://unfccc.int/documents/271493 , 2021.

**************************************************************************
Step (2) select dates and do annual mean
***************************************************************************
 For all models we
  1) extract nbppft, nbp and landCoverFrac files (if available) over 1990-2021 
  2) do annual mean 

nbppft = nbp per plant functional type

**************************************************************************
Step (3) Intact and Non Intact forest NBP from models that provide nbppft.
 - The models are: 'CLASSIC','YIBs','CABLE-POP','JSBACH', 'ISBA-CTRIP'
 - ISBA-CTRIP is not yet uploaded in the server at the time of writing this but the method is included here
***************************************************************************

  1) From landCoverFrac and nbppft we computed mean forest nbp (kg/m2/s)for each gridcell.
     -  ForestNBP= Sum(ForestPFTfrac * Forestnbppft)/sum(ForestPFTfrac) 

  2) Compute mean forest nbp for ISBA-CTRIP model.
     -  nbpTree=nppTree-rhTree-DisturbancesTree
     - where:   DisturbancesTree=fCleach+fFire
     - We assume most of fFire and fCleach originates from forest, if forest exists in the gridcell.
     - we then do same as 1) above.

  3) If low spatial resolution regrid into 0.5x0.5 deg using conservative remapping approach.

  4) Since the unit of forest NBP is kg/m2/s we multiply it by Intact and NonIntact forest area
     that came from the netcdf file described in "step (1)" and number of seconds in the year to get "kg/gridcell/yr"
 
*********************************************************************************
Step (4) Intact and Non Intact forest NBP from models that did not provide nbppft
         but provide landCoverFrac.
 - The models are: 'LPX-Bern','OCN','JULES','VISIT','VISIT-NIES','SDGVM'
*********************************************************************************
  1) If low spatial resolution regrid nbp and landCoverFrac into 0.5x0.5 deg.

  2) for each model and gridcell, we compute the ratio between observed and TRENDY-v11 S2 (from landCoverFrac) forest cover. Somes models did not provide S2 landCoverFrac but did it for S3. In this case we used the first year of S3 landCoverFrac. 

  3) multiply simulated nbp by this ratio, land area and number of seconds in the year
    ==> from kg/m2/s to kg/gridcell/yr

  4) Split into Intact and Non-Intact forest NBP using "IntactAndNonIntactForest_0.5deg.nc" 
     "see step (1)".
  

*********************************************************************************************************
Step (5) Intact and Non Intact forest NBP from models that neither provide nbppft nor landCoverFrac.
 - The models are: 'IBIS','CLM5.0','ORCHIDEE','ISAM','DLEM','LPJ-GUESS','LPJ'

NB: LPJ-GUESS provide landCoverFrac but because of the specificity of this model we used it in this step. Indeed, the sum of PFTs fraction is equal to 1 in all TRENDY models except LPJ-GUESS which allow having different PFts in the same place. For exampl, grass bellow small tree and small tree below tall tree. To be coherent with other models they provide landCoverFrac file that represent an estimate of the foliage projected cover for each PFTs. This file  should not be used to scale any of the LPJ-GUESS per pft data.
**********************************************************************************************************
  1) If low spatial resolution regrid into 0.5x0.5 deg

  2) We use the ratio between observed forest cover and median of the 10 TRENDY S2 models. This ratio is stored in
     "IntactAndNonIntactForest_0.5deg.nc" NetCDF file. See Step (1.6).

  3) multiply simulated nbp by this ratio, land area and number of seconds in the year
    ==> from kg/m2/s to kg/gridcell/yr

  4) Split into Intact and Non-Intact forest NBP using "IntactAndNonIntactForest_0.5deg.nc", see step (1).

  5) We sum over all gridcells to obtain the global estimates for fluxes in intact and non-intact forests.
  
  



- Contact: ram.alkama[at]hotmail.fr
- last update: 09/09/2022
