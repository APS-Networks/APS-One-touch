import constants
from bf_sde import load_bf_sde_profile
from common import get_selected_profile_name, \
    get_sde_pkg_abs_path, get_bsp_pkg_abs_path, \
    is_sim_profile_selected, get_switch_model_from_settings, \
    validate_path_existence
from sal import load_sal_profile
from stratum import load_stratum_profile, get_stratum_home_absolute

def do_basic_path_validation(profile_name):
    # Do basic path verification.
    print('Selected build profile is {}.'.format(profile_name))
    print('Switch model : {}'.format(get_switch_model_from_settings()))
    validate_path_existence(get_sde_pkg_abs_path(), 'Barefoot SDE')
    if not is_sim_profile_selected():
        validate_path_existence(get_bsp_pkg_abs_path(), 'BSP')
    if get_selected_profile_name() in [constants.stratum_sim_profile_name,
                                       constants.stratum_hw_profile_name]:
        validate_path_existence(get_stratum_home_absolute(),'Stratum')

if __name__ == '__main__':
    profile_name = get_selected_profile_name()
    
    do_basic_path_validation(profile_name)

    if profile_name in [constants.stratum_hw_profile_name, constants.stratum_sim_profile_name]:
        load_stratum_profile()
    elif profile_name in [constants.sde_sim_profile_name,constants.sde_hw_profile_name]:
        load_bf_sde_profile()
    elif profile_name in [constants.sal_sim_profile_name,constants.sal_hw_profile_name]:
        load_sal_profile()
    else:
        print('Invalid profile name {} provided in settings.yaml'.format(profile_name))
        
