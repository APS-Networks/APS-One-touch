import logging
import os
import shutil

import common
import constants
from bf_sde import set_sde_env, load_bf_sde_profile
from common import set_env_var, get_sde_home_absolute, \
    get_env_var, \
    get_gb_home_absolute, \
    get_selected_profile_name, read_settings, get_path_relative_to_user_home, \
    get_from_setting_dict, get_selected_profile_dict
from drivers import load_and_verify_kernel_modules
release_dir=''

def set_sal_env():
    print("Setting environment for SAL.")
    if not set_sde_env():
        return False
        exit()
    os.environ['TCMALLOC_LARGE_ALLOC_REPORT_THRESHOLD'] = '64077925800531312640'
    set_env_var(constants.sal_home_env_var_name, get_sal_home_absolute())
    set_env_var(constants.pythonpath_env_var_name, get_sal_home_absolute())
    set_env_var(constants.sde_include_env_var_name,
                get_env_var(constants.sde_install_env_var_name) + '/include')
    set_env_var(constants.gb_home_env_var_name, get_gb_home_absolute())
    global release_dir
    release_dir=get_env_var(constants.sal_home_env_var_name)+'/sal/'

    print('SAL_HOME: {0} \
    \n PYTHONPATH: {1} \
    \n SDE: {2} \
    \n SDE_INSTALL: {3} \
    \n SDE_INCLUDE: {4} \
    \n GB_HOME: {5} \
    \n SAL_RELEASE_DIR:{6} '.format(
        get_env_var(constants.sal_home_env_var_name),
        get_env_var(constants.pythonpath_env_var_name),
        get_env_var(constants.sde_env_var_name),
        get_env_var(constants.sde_install_env_var_name),
        get_env_var(constants.sde_include_env_var_name),
        get_env_var(constants.gb_home_env_var_name),
        release_dir))
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
    prepare_sal_release()



def prepare_sal_release():
    
    try:
        os.mkdir(release_dir)
    except FileExistsError:
        print('Release directory {} already exists, recreated.'.format(release_dir))
        delete_files(release_dir)
        os.mkdir(release_dir)

    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/include/',release_dir+'/include')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/build',release_dir+'/build')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/lib',release_dir+'/lib')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/scripts',release_dir+'/scripts')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/config',release_dir+'/config')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name)+'/proto',release_dir+'/proto')

def delete_files(file):
    try:
        shutil.rmtree(file)
    except FileNotFoundError:
        print('{} already deleted'.format(file))
    except PermissionError:
        i=input('Alert! deleting file {}, y/n ?'.format(file))
        if i=='y':
            os.system('sudo rm -rf {}'.format(file))
    except NotADirectoryError:
        os.system('rm {}'.format(file))

def clean_sal():
    print('Cleaning SAL...')
    
    to_delete = [get_env_var(constants.sal_home_env_var_name)+f for f in ['/bin', '/build', '/logs/', '/CMakeCache.txt', '/Makefile',
                                                                          '/CMakeFiles', '/cmake-build-debug']]

    os.system(
        'make -C {} clean'.format(get_env_var(constants.sal_home_env_var_name)))
    for file in to_delete:
        print('Deteling {}'.format(file))
        delete_files(file)


def run_sal():
    print('Starting SAL reference application...')
    if get_selected_profile_name() == constants.sal_hw_profile_name and not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)

    sal_executable = release_dir + '/build/salRefApp'
    print(release_dir)
    os.system('sudo -E LD_LIBRARY_PATH={0}:{1} {2}'.format(
        get_gb_home_absolute() + '/compilation_root',
        get_sde_home_absolute() + '/install/lib', sal_executable))
    #os.system('sudo -E {}'.format(sal_executable))


def test_sal():
    print("To be integrated")


def take_user_input():
    sal_input = input(
        "Do you want to build(b),clean(c),run(r),test(t),[do_nothing(n)] sal, "
        "Enter one or more action chars in appropriate order i.e. cbr?")

    if 'n' in sal_input or not sal_input:
        # In case user give nasty input like cbrn
        # User meant do nothing in such cases
        return

    set_sal_env()

    for action_char in sal_input:
        if action_char == 'c':
            clean_sal()
        elif action_char == 'r' and get_selected_profile_name() in [
                constants.sal_hw_profile_name,
                constants.sal_sim_profile_name]:
            # Additional checks are for if user selected stratum profile
            # Then there is no need to run sal.
            run_sal()
        elif action_char == 't':
            test_sal()
        elif action_char == 'b':
            build_sal()
        else:
            print(
                "Unrecognised action {0} or action doesn't fit with selected profile {1}.".format(
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
