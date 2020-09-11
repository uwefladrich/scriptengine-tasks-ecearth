"""Tests for helpers/grib_cf_additions.py"""

from iris_grib.grib_phenom_translation import grib1_phenom_to_cf_info

import helpers.grib_cf_additions as additions

def test_update_grib_mappings():
    additions.update_grib_mappings()
    for key, value in additions.additional_mappings.items():
        cf_info = grib1_phenom_to_cf_info(key.t2version, key.centre, key.iParam)
        assert cf_info.standard_name == value.standard_name
