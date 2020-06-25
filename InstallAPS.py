import common
import constants
from bf_sde import load_bf_sde_profile
from common import read_settings, get_selected_profile_name, \
    get_sde_pkg_abs_path, get_bsp_pkg_abs_path, \
    is_sim_profile_selected, get_switch_model_from_settings, \
    validate_path_existence
from sal import load_sal_profile
from stratum import load_stratum_profile, get_stratum_home_absolute

if __name__ == '__main__':
    read_settings()
    profile_name = get_selected_profile_name()
    # Do basic path verification.

    print('Selected build profile is {}.'.format(profile_name))
    print('Switch model : {}'.format(get_switch_model_from_settings()))
    validate_path_existence(get_sde_pkg_abs_path(), 'Barefoot SDE')
    if not is_sim_profile_selected():
        validate_path_existence(get_bsp_pkg_abs_path(), 'BSP')
    if get_selected_profile_name() in [constants.stratum_sim_profile_name,
                                       constants.stratum_hw_profile_name]:
        validate_path_existence(get_stratum_home_absolute(),'Stratum')

    if profile_name in ['stratum_hw_profile', 'stratum_sim_profile']:
        load_stratum_profile()
    elif profile_name == 'sde_sim_profile' or profile_name == 'sde_hw_profile':
        load_bf_sde_profile()
    else:
        load_sal_profile()
