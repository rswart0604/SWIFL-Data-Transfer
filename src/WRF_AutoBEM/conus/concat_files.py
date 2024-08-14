import xarray as xr, numpy as np, wrf, psutil, os, gc

proc = psutil.Process(os.getpid())

WRF_FILES_DIR = '/scratch/rswart/conus404'
FILES = [os.path.join(WRF_FILES_DIR, x) for x in os.listdir(WRF_FILES_DIR)]

print(proc.memory_info().rss)

b =['ACDEWC', 'ACDRIPR', 'ACDRIPS', 'ACECAN', 'ACEDIR', 'ACETLSM', 'ACETRAN', 'ACEVAC', 'ACEVB', 'ACEVC', 'ACEVG', 'ACFROC', 'ACFRZC', 'ACGHB', 'ACGHFLSM', 'ACGHV', 'ACINTR', 'ACINTS', 'ACIRB', 'ACIRC', 'ACIRG', 'ACLHFLSM', 'ACLWDNB', 'ACLWDNBC', 'ACLWDNLSM', 'ACLWDNT', 'ACLWDNTC', 'ACLWUPB', 'ACLWUPBC', 'ACLWUPLSM', 'ACLWUPT', 'ACLWUPTC', 'ACMELTC', 'ACPAHB', 'ACPAHG', 'ACPAHLSM', 'ACPAHV', 'ACPONDING', 'ACQLAT', 'ACQRF', 'ACRAINLSM', 'ACRAINSNOW', 'ACRUNSB', 'ACRUNSF', 'ACSAGB', 'ACSAGV', 'ACSAV', 'ACSHB', 'ACSHC', 'ACSHFLSM', 'ACSHG', 'ACSNBOT', 'ACSNFRO', 'ACSNOM', 'ACSNOWLSM', 'ACSNSUB', 'ACSUBC', 'ACSWDNB', 'ACSWDNBC', 'ACSWDNLSM', 'ACSWDNT', 'ACSWDNTC', 'ACSWUPB', 'ACSWUPBC', 'ACSWUPLSM', 'ACSWUPT', 'ACSWUPTC', 'ACTHROR', 'ACTHROS', 'ACTR', 'ALBEDO', 'CANICE', 'CANWAT', 'EMISS', 'FORCPLSM', 'FORCQLSM', 'FORCTLSM', 'FORCWLSM', 'FORCZLSM', 'GRAUPEL_ACC_NC', 'HFX', 'I_ACLWDNB', 'I_ACLWDNBC', 'I_ACLWDNT', 'I_ACLWDNTC', 'I_ACLWUPB', 'I_ACLWUPBC', 'I_ACLWUPT', 'I_ACLWUPTC', 'I_ACSWDNB', 'I_ACSWDNBC', 'I_ACSWDNT', 'I_ACSWDNTC', 'I_ACSWUPB', 'I_ACSWUPBC', 'I_ACSWUPT', 'I_ACSWUPTC', 'LAI', 'LH', 'LWDNB', 'LWDNBC', 'LWDNT', 'LWDNTC', 'LWUPB', 'LWUPBC', 'LWUPT', 'LWUPTC', 'MLCAPE', 'MLCINH', 'MLLCL', 'MU', 'MUCAPE', 'MUCINH', 'OLR', 'P', 'PBLH', 'PREC_ACC_NC', 'PWAT', 'QFX', 'QRFS', 'QSLAT', 'QSPRINGS', 'QVAPOR', 'RAINNCV', 'RECH', 'REFL_10CM', 'REFL_1KM_AGL', 'REFL_COM', 'SBCAPE', 'SBCINH', 'SBLCL', 'SEAICE', 'SH2O', 'SMCWTD', 'SMOIS', 'SNICE', 'SNLIQ', 'SNOW', 'SNOWC', 'SNOWENERGY', 'SNOWH', 'SNOW_ACC_NC', 'SOILENERGY', 'SR', 'SRH01', 'SRH03', 'SST', 'SSTSK', 'SWDNB', 'SWDNBC', 'SWDNT', 'SWDNTC', 'SWUPB', 'SWUPBC', 'SWUPT', 'SWUPTC', 'TG', 'TH2', 'TK', 'TRAD', 'TSK', 'TSLB', 'TSNO', 'TV', 'U', 'USHR1', 'USHR6', 'UST', 'U_BUNK', 'V', 'VSHR1', 'VSHR6', 'V_BUNK', 'W', 'ZSNSO', 'ZWT', 'totalIce', 'totalLiq', 'totalVap', 'index_snow_layers_stag', 'index_snso_layers_stag', 'index_soil_layers_stag']

LAT_MIN, LAT_MAX = 31.4, 36.654
LON_MAX, LON_MIN = -108.9, -114.657

import time
for f in FILES[30:]:
    old = time.time()
    d = xr.open_dataset(f, chunks='auto', drop_variables=b)
    print(f'read after {time.time()-old}')
    mask = ((d['XLAT'] > LAT_MIN) & (d['XLAT'] < LAT_MAX) & (d['XLONG'] > LON_MIN) & (d['XLONG'] < LON_MAX)).compute()
    print(f'mask after {time.time()-old}')
    dd = d.where(mask, drop=True)
    dd.to_netcdf(f'{f}'.replace('.nc', '_modified.nc').replace('/conus404/', '/conus404small/'))
    print(f'to file after {time.time()-old}')
    print(proc.memory_info().rss)

