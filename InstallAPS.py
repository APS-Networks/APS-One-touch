import common
from bf_sde import load_bf_sde_profile
from common import read_settings, get_selected_profile_name
from sal import load_sal_profile
from stratum import load_stratum_profile

if __name__ == '__main__':
    read_settings()
    profile_name = get_selected_profile_name()
    print('Selected build profile is {}.'.format(profile_name))

    if profile_name == 'stratum_profile':
        load_stratum_profile()
    elif profile_name == 'sde_sim_profile' or profile_name == 'sde_hw_profile':
        load_bf_sde_profile()
    else:
        load_sal_profile()
