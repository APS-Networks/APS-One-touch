import os
import shutil

from common import append_to_env_var, get_env_var, get_path_relative_to_user_home, get_sde_install_dir_absolute, get_selected_profile_dict, get_selected_profile_name, read_settings, set_env_var
import common   
import constants
from drivers import load_and_verify_kernel_modules
from sal import load_sal_profile,  set_sal_runtime_env


def start_stratum():
    print("Starting Stratum....")
    stratum_start_cmd_bsp_less = 'sudo {0}/bazel-bin/stratum/hal/bin/barefoot/stratum_bf \
    --external_stratum_urls=0.0.0.0:28000 \
    --grpc_max_recv_msg_size=256 \
    --bf_sde_install={1} \
    --persistent_config_dir={2} \
    --forwarding_pipeline_configs_file={2}/p4_pipeline.pb.txt \
    --chassis_config_file={2}/chassis_config.pb.txt \
    --write_req_log_file={2}/p4_writes.pb.txt \
    --bf_switchd_cfg={0}/stratum/hal/bin/barefoot/tofino_skip_p4_no_bsp.conf'.format(
        get_env_var(constants.stratum_home_env_var_name),
        get_env_var(constants.bf_sde_install_env_var_name),
        get_env_var(constants.stratum_config_env_var_name)
    )

    append_to_env_var(constants.ld_lib_path_env_var_name,common.get_gb_lib_home_absolute())

    stratum_start_cmd_bsp = 'sudo LD_LIBRARY_PATH={3} {0}/bazel-bin/stratum/hal/bin/barefoot/stratum_bf \
        --external_stratum_urls=0.0.0.0:28000 \
        --grpc_max_recv_msg_size=256 \
        --bf_sde_install={1} \
        --persistent_config_dir={2} \
        --forwarding_pipeline_configs_file={2}/p4_pipeline.pb.txt \
        --chassis_config_file={2}/chassis_config.pb.txt \
        --write_req_log_file={2}/p4_writes.pb.txt \
        --bf_sim'.format(
        get_env_var(constants.stratum_home_env_var_name),
        get_env_var(constants.bf_sde_install_env_var_name),
        get_env_var(constants.stratum_config_env_var_name),
        get_env_var(constants.ld_lib_path_env_var_name)
    )

    if not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)

    
    os.chdir(get_env_var(constants.stratum_home_env_var_name))
    print('Current dir: {}'.format(os.getcwd()))
    if get_stratum_mode() == 'bsp-less':
        print("Starting Stratum in bsp-less mode...")
        print("Executing command {}".format(stratum_start_cmd_bsp_less))
        shutil.copyfile(get_env_var(
        constants.stratum_home_env_var_name) + '/stratum/hal/config/x86-64-stordis-bf2556x-1t-r0/port_map.json',
        get_env_var(
        constants.bf_sde_install_env_var_name) + '/share/port_map.json')
        os.system(stratum_start_cmd_bsp_less)
    else:
        print("Starting Stratum in bsp mode...")
        print("Executing command {}".format(stratum_start_cmd_bsp))
        os.system(stratum_start_cmd_bsp)


def clone_stratum():
    os.system('git clone {}'.format(
        get_stratum_profile_details_dict().get('stratum_repo')))


def set_stratum_env():
    if not set_sal_runtime_env():
        exit(0)
    print('Setting environment for stratum.')
    append_to_env_var(constants.ld_lib_path_env_var_name,
                      "/{0}/lib:/lib/x86_64-linux-gnu".format(
                          get_env_var(constants.sde_install_env_var_name)))
    set_env_var(constants.pi_install_env_var_name,
                get_sde_install_dir_absolute())
    set_env_var(constants.stratum_config_env_var_name,
                get_stratum_config_dir_absolute())
    set_env_var(constants.stratum_home_env_var_name,
                get_stratum_home_absolute())
    # set_env_relative_to_user_home('ONLP_INSTALL', "/onlp-dev_1.0.1_amd64" )
    # required to compile stratum
    set_env_var(constants.bf_sde_install_env_var_name,
                get_sde_install_dir_absolute())

    print('Env for starting Stratum :\n{0}\n{1}\n{2}\n{3}\n{4}\n{5}'.format(
        '{} {}'.format(constants.bf_sde_install_env_var_name, get_env_var(
            constants.bf_sde_install_env_var_name)),
        '{} {}'.format(constants.ld_lib_path_env_var_name,
                       get_env_var(constants.ld_lib_path_env_var_name)),
        '{} {}'.format(constants.pi_install_env_var_name,
                       get_env_var(constants.pi_install_env_var_name)),
        '{} {}'.format(constants.stratum_config_env_var_name,
                       get_env_var(constants.stratum_config_env_var_name)),
        '{} {}'.format(constants.stratum_home_env_var_name,
                       get_env_var(constants.stratum_home_env_var_name)),
        '{} {}'.format(constants.sal_home_env_var_name,
                       get_env_var(constants.sal_home_env_var_name))
    ))


def clean_startum():
    print('Cleaning stratum.')
    stratum_clean_cmd = 'bazel clean'
    os.chdir(get_stratum_home_absolute())

    print('Executing : {}'.format(stratum_clean_cmd))
    os.system(stratum_clean_cmd)


def build_stratum():
    print('Building stratum...')
    stratum_build_command = 'bazel build //stratum/hal/bin/barefoot:stratum_bf'
                            #':stratum_bf --define phal_with_gb=true '
    if get_stratum_mode() == 'bsp':
        stratum_build_command = stratum_build_command + ' --define phal_with_onlp=false --define sde_ver=9.1.0 '
    os.chdir(get_stratum_home_absolute())
    print('Executing : {}'.format(stratum_build_command))
    os.system(stratum_build_command)


def clean_stratum():
    print('Cleaning stratum...')
    print('Current working dir {}'.format(os.getcwd()))
    stratum_clean_cmd = 'bazel clean'
    os.chdir(get_env_var(constants.stratum_home_env_var_name))
    print('Executing : {}'.format(stratum_clean_cmd))
    os.system(stratum_clean_cmd)


def get_stratum_mode():
    get_stratum_profile_details_dict().get('mode')


def get_stratum_profile_dict():
    if get_selected_profile_name() in [constants.stratum_hw_profile_name,
                                       constants.stratum_sim_profile_name]:
        return get_selected_profile_dict()


def get_stratum_profile_details_dict():
    return get_stratum_profile_dict().get('details')


def get_stratum_home_absolute():
    return get_path_relative_to_user_home(
        get_stratum_profile_details_dict().get('stratum_home'))


def get_stratum_config_dir_absolute():
    stratum_config_dir=get_stratum_profile_details_dict().get('stratum_config')
    if stratum_config_dir is None:
        return common.dname+'/stratum_config/'
    else:
        return get_path_relative_to_user_home(
            get_stratum_profile_details_dict().get('stratum_config'))


def load_stratum_profile():
    load_sal_profile()
    take_user_input()


def take_user_input():
    stratum_input = input(
        "Do you want to build(b),clean(c),run(r),[do_nothing(n)] stratum, "
        "Enter one or more action chars in appropriate order i.e. cbr?")

    if 'n' in stratum_input or not stratum_input:
        # In case user give nasty input like cbrn
        # User meant do nothing in such cases
        return
    
    set_stratum_env()
    for action_char in stratum_input:      
        if action_char == 'c':
            clean_stratum()
        elif action_char == 'r':
            start_stratum()
        elif action_char == 'b':
            build_stratum()
        else:
            print(
                "Unrecognised action {} .".format(action_char))


if __name__ == '__main__':
    read_settings()
    load_stratum_profile()
