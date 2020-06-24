import iris_grib._grib_cf_map
from iris_grib._grib_cf_map import G1LocalParam, CFName

additional_mappings = {
    G1LocalParam(1, 128, 98, 228): CFName('lwe_thickness_of_precipitation_amount', None, 'm'),
    G1LocalParam(1, 128, 98, 144): CFName('lwe_thickness_of_snowfall_amount', None, 'm'),
    G1LocalParam(1, 128, 98, 176): CFName('surface_net_downward_shortwave_flux', None, 'J m-2'),
    G1LocalParam(1, 128, 98, 177): CFName('surface_net_upward_longwave_flux', None, 'J m-2'),
    G1LocalParam(1, 128, 98, 178): CFName('toa_net_upward_shortwave_flux', None, 'J m-2'),
    G1LocalParam(1, 128, 98, 179): CFName('toa_outgoing_longwave_flux', None, 'J m-2'),
    G1LocalParam(1, 128, 98, 146): CFName('surface_upward_sensible_heat_flux', None, 'J m-2'),
    G1LocalParam(1, 128, 98, 147): CFName('surface_upward_latent_heat_flux', None, 'J m-2'),
}

def update_grib_mappings():
   iris_grib._grib_cf_map.GRIB1_LOCAL_TO_CF.update(additional_mappings)
   iris_grib.grib_phenom_translation._GRIB1_CF_TABLE = iris_grib.grib_phenom_translation._make_grib1_cf_table()