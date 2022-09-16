""" //----------------------------------------------------------------//
   //----------------------------------------------------------------//
  //Intact and Non Intact forest NBP from TRENDY-v11 S2 simulations //
 //----------------------------------------------------------------//
//----------------------------------------------------------------//
************************************
 Step (1) Create an auxiliary file 
************************************
The following steps are done in Google Earth Engine (GEE) platform:

  1) Convert Hansen tree cover (30m spatial resolution) to forest cover. 
     To do this, FAO definition of forest (more that 20% tree cover and a minimum continuity of 0.5 ha) is used.
  2) Intact and Non-Intact "Forest" masks came from Popatov except over Canada and Brazil from where we got more acurate masks.
       ==> Popatov mask was updated over Brazil and Canada
  3) Merge the two datasets to get the Intact and Non-Intact forest area per gridcells of around 30m spatial resolution.
  4) Redrid the data to 0.5 degree spatial resolution. 
     Because of the computational issue, this has been done in two steps. From 30m to 0.01 degree, then from 0.01 to 0.5 degree.
  5) The 0.5 degree Intact and Non-Intact forest area is saved in "IntactAndNonIntactForest_0.5deg.nc" NetCDF file.
     The javascript code "IntactAndNonIntactForest_0.5deg.js" that is used to generate this file is available in the:
     https://github.com/RamAlkama/LandCarbonBudget_IntactAndNonIntactForest 

This last step is done outside GEE
  6) We compute the ratio between observed forest cover and the median forest cover coming from the 10 TRENDY S2 models that provide 
     landCoverFrac. Models are:'CLASSIC','YIBs','CABLE-POP','JSBACH', 'ISBA-CTRIP','LPX-Bern','OCN','JULES','VISIT','VISIT-NIES','SDGVM'
     This variable is also included in the "IntactAndNonIntactForest_0.5deg.nc" NetCDF file and used in the Step (5)

The NetCDF is availble via request to ram.alkama[at]hotmail.fr

    
**************************************************************************
Step (2) select dates and do annual mean
***************************************************************************
 For all models we
  1) extract nbppft, nbp and landCover files over 1990-2021 
  2) do annual mean 

**************************************************************************
Step (3) Intact and Non Intact forest NBP from models that provide nbppft
           Models: 'CLASSIC','YIBs','CABLE-POP','JSBACH', 'ISBA-CTRIP'
***************************************************************************

  1) From landCoverFrac and nbppft we computed mean forest nbp (kg/m2/s)
     for each gridcell ForestNBP= Sum(ForestPFTfrac * Forestnbppft)/sum(ForestPFTfrac)

  2) Compute mean forest nbp for ISBA-CTRIP model 
     nbpTree=nppTree-rhTree-DisturbancesTree
     where:DisturbancesTree=fCleach+fFire
     We assume most of fFire and fCleach originates from forest, if forest exists in the gridcell.
     we then do same as 1) above

  3) If low spatial resolution regrid into 0.5x0.5 deg

  4) Since the unit of forest NBP is kg/m2/s we multiply it by Intact and NonIntact forest area
     that came from the netcdf file described in "step (1)" and number of seconds in the year to get "kg/gridcell/yr"
 
*********************************************************************************
Step (4) Intact and Non Intact forest NBP from models that did not provide nbppft
         but provide landCoverFrac
         Models: 'LPX-Bern','OCN','JULES','VISIT','VISIT-NIES','SDGVM'
*********************************************************************************
  1) If low spatial resolution regrid into 0.5x0.5 deg

  2) for each model and gridcell, we compute the ratio between observed and TRENDY-v11 S2 forest cover

  3) multiply simulated nbp by this ratio, land area and number of seconds in the year
    ==> from kg/m2/s to kg/gridcell/yr

  4) Split into Intact and Non-Intact forest NBP using "IntactAndNonIntactForest_0.5deg.nc" 
     "see step (1)"
  

*********************************************************************************************************
Step (5) Intact and Non Intact forest NBP from models that neither provide nbppft nor landCoverFrac
         Models: 'IBIS','CLM5.0','ORCHIDEE','ISAM','DLEM','LPJ-GUESS'

NB: LPJ-GUESS provide landCoverFrac but because of the specificity of this model we used it in this step
**********************************************************************************************************
  1) If low spatial resolution regrid into 0.5x0.5 deg

  2) We use the ratio between observed and median of 10 TRENDY S2 models that is stored in
     "IntactAndNonIntactForest_0.5deg.nc" NetCDF file. See Step (1.6)

  3) multiply simulated nbp by this ratio, land area and number of seconds in the year
    ==> from kg/m2/s to kg/gridcell/yr

  4) Split into Intact and Non-Intact forest NBP using "IntactAndNonIntactForest_0.5deg.nc" 
     "see step (1)"



Contact: ram.alkama@hotmail.fr
last update: 09/09/2022

"""
import cdms2 as cdms, os, glob, numpy as N, MV2 as MV


cdms.setNetcdfShuffleFlag(0)
cdms.setNetcdfDeflateFlag(0)
cdms.setNetcdfDeflateLevelFlag(0)


# -----------------------------------------
# Step (2) select dates and do annual mean
# -----------------------------------------

# PreProcess data from monthly 1700-2019 to yearly 1990-2021
if True:
  for var in ['nbppft','landCoverFrac','nbp']:
    for fil in glob.glob("*%s.nc"%var):
      filo='/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/'+fil
      if not os.path.exists(filo):
        os.system("cdo -P 12 yearmean -selyear,1990/2021 %s %s"%(fil,filo))


# ---------------------------------------------------------------------------------
# Step (3) Intact and Non Intact forest NBP from models that provide nbppft
# ---------------------------------------------------------------------------------

# forest pfts       
listepfts={'ORCHIDEE':[1,2,3,4,5,6,7,8],'ORCHIDEE-CNP':[1,2,3,4,5,6,7,8],'JSBACH':[2,3,4,5],'CLASS-CTEM':[0,1,2,3,4],'DLEM':[4,5,6,7,8,9,10,11],
           'LPJ-GUESS':[0,1,2,3,4,5,6,7,8,9],'OCN':[1,2,3,4,5,6,7,8],'CABLE-POP':[0,1,2,3],'ISAM':[0,1,2,3,4,13,14,15,16,17,19,23],
           'ORCHIDEEv3':[1,2,3,4,5,6,7,8],'SDGVM':[6,7,8,9],'JULES':[0,1,2,3,4],'CLASSIC':[0,1,2,3,4],'CLASSIC-N':[0,1,2,3,4],
           'VISIT':[0,1,2,3,4,5,6,7],'VISIT-NIES':[0,1,2,3,4,5,6,7],'YIBs':[0,1,2],'LPX-Bern':[0,1,2,3,4,5,6,7],'CLM5.0':[1,2,3,4,5,6,7,8],'LPJ':[0,1,2,3,4,5]} 


# LPX-Bern and 'VISIT': nbppft over forest are missing
if True:
 for model in ['CLASSIC','YIBs','CABLE-POP','JSBACH']: #'OCN','CLASSIC-N'
  var='nbppft'
  if model=='CLASSIC':var='nbp'
  print model
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/%s_S2_nbppft.nc'%model)
  nbppft=f(var)
  f.close()
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/%s_S2_landCoverFrac.nc'%model)
  pftFrac=f('landCoverFrac',squeeze=1)
  f.close()
  AXIS=nbppft[:,0,:,:].getAxisList()
  nbp,forestFrac=N.zeros(nbppft[:,0,:,:].shape),N.zeros(nbppft[:,0,:,:].shape)
  if len(pftFrac.shape)==3:
   for pft in listepfts[model]:
     for tt in range(nbppft.shape[0]):
       if model =='CABLE-POP':
         nbp[tt,:,:]=nbp[tt,:,:]+MV.where(nbppft[tt,pft,:,:].mask,0,nbppft[tt,pft,:,:])*MV.where(pftFrac[pft,:,:].mask,0,pftFrac[pft,:,:])
         forestFrac[tt,:,:]=forestFrac[tt,:,:]+MV.where(pftFrac[pft,:,:].mask,0,pftFrac[pft,:,:])
       else:
         nbp[tt,:,:]=nbp[tt,:,:]+nbppft[tt,pft,:,:]*pftFrac[pft,:,:]
         forestFrac[tt,:,:]=forestFrac[tt,:,:]+pftFrac[pft,:,:]
  else:
   for pft in listepfts[model]:
    nbp=nbp[:,:,:]+nbppft[:,pft,:,:]*pftFrac[:,pft,:,:]
    forestFrac=forestFrac[:,:,:]+pftFrac[:,pft,:,:]
  nbp=MV.where(forestFrac>0,nbp/forestFrac,0)
  nbp=MV.masked_equal(nbp,0)
  nbp=cdms.createVariable(nbp,fill_value = 1.e+20,dtype='d',axes =AXIS) 
  nbp.units="kg m-2 s-1"
  nbp.long_name = "Carbon Mass Flux out of Atmosphere due to Net Biospheric Production on Forest"
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/%s_NBP_forest_1990_2021.nc'%model,'w')
  f.write(nbp,id='nbp')
  f.close()


# --------------------
#   ISBA-CTRIP model
# --------------------

if False: # False because the data is not yet available, turn it to True when exists 
  # PreProcess data from monthly 1700-2019 to yearly 1990-2021
  for fil in glob.glob("ISBA*.nc"):
    filo='/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/'+fil
    if not os.path.exists(filo):
      os.system("cdo -P 12 yearmean -selyear,1990/2021 %s %s"%(fil,filo))

  print model
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/%s_S2_nppTree.nc'%model)
  nppTree=f('nppTree')
  f.close()
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/%s_S2_rhTree.nc'%model)
  rhTree=f('rhTree')
  f.close()
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/%s_S2_fFire.nc'%model)
  fFire=f('fFire')
  f.close()
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/%s_S2_fCLeach.nc'%model)
  fCleach=f('fCLeach')
  f.close()
  AXIS=nppTree.getAxisList()
  DisturbancesTree=(fCleach+fFire)
  nbpTree=nppTree-rhTree-MV.where(nppTree>-1,DisturbancesTree,0)
  nbpTree=cdms.createVariable(nbpTree,fill_value = 1.e+20,dtype='d',axes =AXIS) 
  nbpTree.units="kg m-2 s-1"
  nbpTree.long_name = "Carbon Mass Flux out of Atmosphere due to Net Biospheric Production on Forest"
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/%s_NBP_forest_1990_2021.nc'%model,'w')
  f.write(nbpTree,id='nbp')
  f.close()

# --------------------
# - If low spatial resolution regrid into 0.5x0.5 deg
# - Split forest NBP into Intact and Non Intact Forest NBP
# --------------------
os.chdir('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v11/Workdir/')

if True:
 for model in ['CLASSIC','YIBs','CABLE-POP','JSBACH']:#'CLASSIC-N','OCN','ISBA-CTRIP']:
   print model
   fil='%s_NBP_forest_1990_2021.nc'%model
   f=cdms.open(fil)
   var='nbp'#f.listvariable()[0]
   v=f[var]
   nlons=v.shape[2]
   f.close()
   if nlons==720:
     filin=fil
   else:
     filin=fil[:-3]+'_05deg.nc'
     os.system('cdo -P 20 remapcon,targetgrid %s %s'%(fil,filin))
   f=cdms.open(filin)
   nbp=f('nbp')*86400.*365    # from kgC/m2/s to kgC/m2/yr
   f.close()
   AXIS=nbp.getAxisList()

   f=cdms.open('IntactAndNonIntactForest_0.5deg.nc')
   Intact=f('IntactForestArea')
   NonIntact=f('NonIntactForestArea')
   f.close()

   ff=cdms.open('%s_Intact_and_NonIntact_forestNBP_1990_2021_05deg.nc' %model,'w')
   Intact=cdms.createVariable(nbp*Intact,fill_value = 1.e+20,dtype='f',axes =AXIS)
   Intact.units="kg/gridcell/yr"
   ff.write(Intact,id='Intact')
   NonIntact=cdms.createVariable(nbp*NonIntact,fill_value = 1.e+20,dtype='f',axes =AXIS)
   NonIntact.units="kg/gridcell/yr"
   ff.write(NonIntact,id='NonIntact')
   ff.close()


# ----------------------------------------------------------------------
# Step (4) Models that did not provide nbppft but provide landCoverFrac
# ----------------------------------------------------------------------

if True:
 os.system('rm -f  landCoverFrac.nc nbp.nc')
 for fil in glob.glob("*landCoverFrac.nc"):
   model=fil.split('_')[0]
   #print model
   if model not in ['CLASSIC','YIBs','CABLE-POP','JSBACH']:
     f=cdms.open(fil)
     var='landCoverFrac'#f.listvariable()[0]
     v=f[var].getLongitude()
     nlons=len(v)
     f.close()
     print model, nlons
     if nlons==720:
       filfrac=fil
       filnbp=fil.replace('landCoverFrac','nbp')
     else:
       filfrac='landCoverFrac.nc'
       filnbp='nbp.nc'
       os.system('cdo -P 20 remapcon,targetgrid %s %s'%(fil,filfrac))
       os.system('cdo -P 20 remapcon,targetgrid %s %s'%(fil.replace('landCoverFrac','nbp'),filnbp))

     f=cdms.open(filnbp)
     nbp=f('nbp',lat=(-60,90),lon=(-180,180))*86400.*365    # from kgC/m2/s to kgC/m2/yr
     f.close()
     AXIS=nbp.getAxisList()
     f=cdms.open(filfrac)
     if model=='CABLE-POP':
         pftFrac=f('landCoverFrac',lat=(-60,90),lon=(-180,180),squeeze=1)
     else:
         pftFrac=f('landCoverFrac',cdms.timeslice(0,1),lat=(-60,90),lon=(-180,180),squeeze=1)
     f.close()

     forestFrac=N.zeros(nbp[0,:,:].shape)
     for pft in listepfts[model]:
       if model =='CABLE-POP':
         forestFrac[:,:]=forestFrac[:,:]+MV.where(pftFrac[pft,:,:].mask,0,pftFrac[pft,:,:])
       else:
         forestFrac[:,:]=forestFrac[:,:]+pftFrac[pft,:,:]
     if model in ['VISIT-NIES','VISIT']:forestFrac=forestFrac/100.
     forestFrac=MV.masked_less(forestFrac,0)
     f=cdms.open('IntactAndNonIntactForest_0.5deg.nc')
     All=f('ForestArea',lat=(-60,90),lon=(-180,180))
     Intact=MV.where(All!=0,f('IntactForestArea',lat=(-60,90),lon=(-180,180))/All,0)
     NonIntact=MV.where(All!=0,f('NonIntactForestArea',lat=(-60,90),lon=(-180,180))/All,0)
     landFrac=f('LandCoverFrac',lat=(-60,90),lon=(-180,180))
     cell_area=f('cell_area',lat=(-60,90),lon=(-180,180))
     f.close()
     landArea=cell_area*landFrac
     print N.nanmin(forestFrac),N.nanmax(forestFrac)
     ratio=MV.where(forestFrac!=0,All/(forestFrac*landArea),0) # (observed forest area)/(simulated forest area)
     ratio=MV.where(ratio<0,0,ratio)
     ratio=MV.where(ratio>2,2,ratio)
     ratio=cdms.createVariable(ratio,fill_value = 1.e+20,dtype='f',axes =All.getAxisList())
     #ratio=cdms.createVariable(forestFrac*landArea,fill_value = 1.e+20,dtype='f',axes =All.getAxisList())
     Intact=cdms.createVariable(Intact,fill_value = 1.e+20,dtype='f',axes =All.getAxisList())
     NonIntact=cdms.createVariable(NonIntact,fill_value = 1.e+20,dtype='f',axes =All.getAxisList())
    
     ff=cdms.open('%s_Intact_and_NonIntact_forestNBP_1990_2021_05deg.nc' %model,'w')
     Intact=nbp*Intact*landArea*ratio
     Intact=MV.masked_greater(MV.masked_less(Intact,-1.e14),1.e14)
     Intact=cdms.createVariable(Intact,fill_value = 1.e+20,dtype='f',axes =nbp.getAxisList())
     Intact.units="kg/gridcell/yr"
     ff.write(Intact,id='Intact')
     NonIntact=nbp*NonIntact*landArea*ratio
     NonIntact=MV.masked_greater(MV.masked_less(NonIntact,-1.e14),1.e14)
     NonIntact=cdms.createVariable(NonIntact,fill_value = 1.e+20,dtype='f',axes =nbp.getAxisList())
     NonIntact.units="kg/gridcell/yr"
     ff.write(NonIntact,id='NonIntact')
     #ff.write(ratio,id='ratio')
     #ff.write(nbp*landArea,id='totalNBP')
     ff.close()

   os.system('rm -f  landCoverFrac.nc nbp.nc')

# ---------------------------------------------------------------
# Step (5) Models that did not provide nbppft and landCoverFrac
# ---------------------------------------------------------------

f=cdms.open('IntactAndNonIntactForest_0.5deg.nc')
All=f('ForestArea',lat=(-60,90),lon=(-180,180))
Intact=MV.where(All!=0,f('IntactForestArea',lat=(-60,90),lon=(-180,180))/All,0)
NonIntact=MV.where(All!=0,f('NonIntactForestArea',lat=(-60,90),lon=(-180,180))/All,0)
landFrac=f('LandCoverFrac',lat=(-60,90),lon=(-180,180))
cell_area=f('cell_area',lat=(-60,90),lon=(-180,180))
ratio=f('ratio',lat=(-60,90),lon=(-180,180))
f.close()
landArea=cell_area*landFrac

Intact=cdms.createVariable(Intact,fill_value = 1.e+20,dtype='f',axes =All.getAxisList())
NonIntact=cdms.createVariable(NonIntact,fill_value = 1.e+20,dtype='f',axes =All.getAxisList())

Intact=Intact*landArea*ratio
NonIntact=NonIntact*landArea*ratio

if True :
 os.system('rm -f nbp.nc')
 for fil in glob.glob("*_nbp.nc"):
   model=fil.split('_')[0]
   #print model
   if model in ['IBIS','CLM5.0','ORCHIDEE','ISAM','DLEM','LPJ-GUESS']:
     f=cdms.open(fil)
     var='nbp'
     v=f[var].getLongitude()
     nlons=len(v)
     f.close()
     print model, nlons
     if nlons==720:
       filnbp=fil
     else:
       filnbp='nbp.nc'
       os.system('cdo -P 20 remapcon,targetgrid %s %s'%(fil,filnbp))

     f=cdms.open(filnbp)
     nbp=f('nbp',lat=(-60,90),lon=(-180,180))*86400.*365    # from kgC/m2/s to kgC/m2/yr
     f.close()
     AXIS=nbp.getAxisList()
     
     ff=cdms.open('%s_Intact_and_NonIntact_forestNBP_1990_2021_05deg.nc' %model,'w')
     Inta=nbp*Intact
     Inta=N.ma.masked_invalid(MV.masked_greater(MV.masked_less(Inta,-1.e14),1.e14))
     Inta=cdms.createVariable(Inta,fill_value = 1.e+20,dtype='f',axes =nbp.getAxisList())
     Inta.units="kg/gridcell/yr"
     ff.write(Inta,id='Intact')
     NonInta=nbp*NonIntact
     NonInta=N.ma.masked_invalid(MV.masked_greater(MV.masked_less(NonInta,-1.e14),1.e14))
     NonInta=cdms.createVariable(NonInta,fill_value = 1.e+20,dtype='f',axes =nbp.getAxisList())
     NonInta.units="kg/gridcell/yr"
     ff.write(NonInta,id='NonIntact')
     #ff.write(ratio,id='ratio')
     #totalNBP=N.ma.masked_invalid(nbp*landArea)
     #totalNBP=cdms.createVariable(totalNBP,fill_value = 1.e+20,dtype='f',axes =nbp.getAxisList())
     #totalNBP.units="kg/gridcell/yr"
     #ff.write(totalNBP,id='totalNBP')
     ff.close()

   os.system('rm -f  nbp.nc')


