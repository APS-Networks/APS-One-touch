import logging
import os
import shutil

import common
import constants
from bf_sde import set_sde_env_n_load_drivers, load_bf_sde_profile
from common import delete_files, get_env_var, get_from_setting_dict, get_gb_lib_home_absolute, get_gb_src_home_absolute, get_path_relative_to_user_home, get_sde_home_absolute, get_selected_profile_dict, get_selected_profile_name, read_settings, set_env_var 
get_gb_src_home_absolute, get_path_relative_to_user_home, get_sde_home_absolute, get_selected_profile_dict, 
get_selected_profile_name, read_settings, set_env_var
from drivers import load_and_verify_kernel_modules
from sal_test import execute_sal_tests

def set_sal_env():
    print("Setting environment for SAL.")
    if not set_sde_env_n_load_drivers():
        return False
        exit()
    #os.environ['TCMALLOC_LARGE_ALLOC_REPORT_THRESHOLD'] = '64077925800531312640'
    set_env_var(constants.sal_home_env_var_name, get_sal_home_absolute())
    set_env_var(constants.pythonpath_env_var_name, get_sal_home_absolute())
    set_env_var(constants.sde_include_env_var_name,
                get_env_var(constants.sde_install_env_var_name) + '/include')
    set_env_var(constants.gb_src_home_env_var_name, get_gb_src_home_absolute())
    set_env_var(constants.gb_lib_home_env_var_name, get_gb_lib_home_absolute())

    print('SAL_HOME: {0} \
    \n PYTHONPATH: {1} \
    \n SDE: {2} \
    \n SDE_INSTALL: {3} \
    \n SDE_INCLUDE: {4} \
    \n GB_SRC_HOME: {5} \
    \n GB_LIB_HOME: {6} '.format(
        get_env_var(constants.sal_home_env_var_name),
        get_env_var(constants.pythonpath_env_var_name),
        get_env_var(constants.sde_env_var_name),
        get_env_var(constants.sde_install_env_var_name),
        get_env_var(constants.sde_include_env_var_name),
        get_env_var(constants.gb_src_home_env_var_name),
        get_env_var(constants.gb_lib_home_env_var_name)))
    return True

def set_sal_runtime_env():
    print("Setting environment for SAL runtime.")
    if not set_sde_env_n_load_drivers():
        return False
        exit()
    set_env_var(constants.sal_home_env_var_name, sal_rel_dir)
    print('SAL_HOME: {}'.format(get_env_var(constants.sal_home_env_var_name)))
    # set_env_var(constants.gb_src_home_env_var_name, sal_rel_dir)
    # set_env_var(constants.gb_lib_home_env_var_name, sal_rel_dir+'/lib')
    # print('SAL_SRC_HOME: {}'.format(get_env_var(constants.sal_src_home_env_var_name)))
    # print('SAL_LIB_HOME: {}'.format(get_env_var(constants.sal_lib_home_env_var_name)))
    return True

def get_sal_home_absolute():
    return get_path_relative_to_user_home(get_sal_home_from_config())


def get_sal_home_from_config():
    return common.settings_dict. \
        get(constants.sal_sw_attr_node).get(constants.sal_home_node)


def get_sal_profile_dict():
    selected_profile = get_selected_profile_dict()
    selected_profile_name = get_selected_profile_name()
    if selected_profile_name in [constants.sal_hw_profile_name,
                                 constants.sal_sim_profile_name]:
        return selected_profile
    elif selected_profile_name == constants.stratum_sim_profile_name:
        return common.settings_dict.get(constants.build_profiles_node).get(
            constants.sal_sim_profile_node)
    elif selected_profile_name == constants.stratum_hw_profile_name:
        return common.settings_dict.get(constants.build_profiles_node).get(
            constants.sal_hw_profile_node)
    else:
        logging.error('There is no selected or associated SAL profile')


def get_sal_profile_details():
    return get_sal_profile_dict().get(constants.details_node)


def build_sal():
    print('Building SAL...')
    os.chdir(get_env_var(constants.sal_home_env_var_name))
    cmake_cmd = 'cmake '

    cmake_cmd += get_env_var(constants.sal_home_env_var_name)
    print('Executing cmake command {}.'.format(cmake_cmd))
    os.system(cmake_cmd)
    os.system('make -C {}'.format(get_env_var(constants.sal_home_env_var_name)))

sal_rel_dir=common.release_dir+'/sal'

def prepare_sal_release():
    
    try:
        os.mkdir(sal_rel_dir)
        print('SAL release directory {} created.'.format(sal_rel_dir))
    except FileExistsError:
        print('SAL Release directory {} already exists, recreated.'.format(sal_rel_dir))
        delete_files(sal_rel_dir)
        os.mkdir(sal_rel_dir)

    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/include/',sal_rel_dir+'/include')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/src/include/',sal_rel_dir+'/src/include')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/build',sal_rel_dir+'/build')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/lib',sal_rel_dir+'/lib')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/scripts',sal_rel_dir+'/scripts')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/config',sal_rel_dir+'/config')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/proto',sal_rel_dir+'/proto')
    
    os.mkdir(sal_rel_dir+'/test')
    shutil.copyfile(get_env_var(constants.sal_home_env_var_name)+'/test/sal_service_test_direct.py',sal_rel_dir+'/test/sal_service_test_direct.py')
    shutil.copyfile(get_env_var(constants.sal_home_env_var_name)+'/sal_services_direct_pb2.py',sal_rel_dir+'/sal_services_direct_pb2.py')
    shutil.copyfile(get_env_var(constants.sal_home_env_var_name)+'/sal_services_direct_pb2_grpc.py',sal_rel_dir+'/sal_services_direct_pb2_grpc.py')
    shutil.copyfile(get_env_var(
        constants.sal_home_env_var_name) + '/sal_services_pb2.py',
                    sal_rel_dir + '/sal_services_pb2.py')
    shutil.copyfile(get_env_var(
        constants.sal_home_env_var_name) + '/sal_services_pb2_grpc.py',
                    sal_rel_dir + '/sal_services_pb2_grpc.py')
    print('SAL release is available at {}'.format(sal_rel_dir))


def clean_sal():
    print('Cleaning SAL...')
    
    to_delete = [get_env_var(constants.sal_home_env_var_name)+f for f in ['/lib', '/bin', '/build', '/logs/', '/CMakeCache.txt', '/Makefile',
                                                                          '/CMakeFiles', '/cmake-build-debug']]
    os.system(
        'make -C {} clean'.format(get_env_var(constants.sal_home_env_var_name)))
    for file in to_delete:
        print('Deteling {}'.format(file))
        delete_files(file)


def run_sal():
    print('Starting SAL reference application...')
    set_sal_runtime_env()
    if get_selected_profile_name() == constants.sal_hw_profile_name and not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)

    sal_executable = sal_rel_dir + '/build/salRefApp'
    sal_run_cmd='sudo -E LD_LIBRARY_PATH={0}:{1}:{2} {3}'.format(
        sal_rel_dir + '/build',
        sal_rel_dir + '/lib',
        get_sde_home_absolute() + '/install/lib', sal_executable)
    print('Running SAL with command: {}'.format(sal_run_cmd))
    os.system(sal_run_cmd)
    #os.system('sudo -E {}'.format(sal_executable))


def test_sal():
    execute_sal_tests()


def take_user_input():
    sal_input = input(
        "SAL : build(b),clean(c),run(r),test(t),[do_nothing(n)], "
        "Enter one or more action chars in appropriate order i.e. cbr?")

    if 'n' in sal_input or not sal_input:
        # In case user give nasty input like cbrn
        # User meant do nothing in such cases
        return

    for action_char in sal_input:
        if action_char == 'c':
            set_sal_env()
            clean_sal()
        elif action_char == 'r':
            run_sal()
        elif action_char == 't':
            test_sal()
        elif action_char == 'b':
            set_sal_env()
            build_sal()
            prepare_sal_release()
        else:
            print(
                "Invalid action {0} or action doesn't fit with selected profile {1}.".format(
                    action_char, get_selected_profile_name()))
    

def load_sal_profile():
    load_bf_sde_profile()
    take_user_input()
    


def just_load_sal():
    """
    When deps of SAL are taken care already, Directly execute this file.
    :return:
    """
    read_settings()
    take_user_input()


if __name__ == '__main__':
    just_load_sal()
