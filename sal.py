import os
import shutil

import common
from bf_sde import set_sde_env, load_bf_sde_profile
from common import set_env_var, get_sde_home_absolute, get_sal_home_absolute, \
    get_env_var, \
    get_gb_home_absolute, \
    get_selected_profile_name, read_settings
from drivers import load_and_verify_kernel_modules


def set_sal_env():
    if not set_sde_env():
        exit()
    os.environ['TCMALLOC_LARGE_ALLOC_REPORT_THRESHOLD'] = '64077925800531312640'
    set_env_var(common.sal_home_env_var_name, get_sal_home_absolute())
    set_env_var(common.pythonpath_env_var_name, get_sal_home_absolute())
    set_env_var(common.sde_env_var_name, get_sde_home_absolute())
    set_env_var(common.sde_install_env_var_name,
                get_env_var(common.sde_env_var_name) + '/install')
    set_env_var(common.sde_include_env_var_name,
                get_env_var(common.sde_install_env_var_name) + '/include')
    set_env_var(common.gb_home_env_var_name, get_gb_home_absolute())

    print('SAL_HOME: {0} \
    \n PYTHONPATH: {1} \
    \n SDE: {2} \
    \n SDE_INSTALL: {3} \
    \n SDE_INCLUDE: {4} \
    \n GB_HOME: {5}'.format(
        get_env_var(common.sal_home_env_var_name),
        get_env_var(common.pythonpath_env_var_name),
        get_env_var(common.sde_env_var_name),
        get_env_var(common.sde_install_env_var_name),
        get_env_var(common.sde_include_env_var_name),
        get_env_var(common.gb_home_env_var_name)))
    return True


def build_sal():
    print('Building SAL...')
    set_sal_env()
    os.chdir(os.environ['SAL_HOME'])
    os.system('cmake {}'.format(os.environ['SAL_HOME']))
    os.system('make -C {}'.format(os.environ['SAL_HOME']))


def clean_sal():
    print('Cleaning SAL...')
    set_sal_env()
    build_dir = os.environ['SAL_HOME'] + '/build'
    log_dir = os.environ['SAL_HOME'] + '/logs/'
    cmake_cache_file = os.environ['SAL_HOME'] + '/CMakeCache.txt'
    make_file = os.environ['SAL_HOME'] + '/Makefile'
    cmake_dir = os.environ['SAL_HOME'] + '/CMakeFiles'
    bin_dir = os.environ['SAL_HOME'] + '/bin'

    os.system('make -C {} clean'.format(os.environ['SAL_HOME']))
    try:
        shutil.rmtree(build_dir)
    except FileNotFoundError:
        print('{} already deleted'.format(build_dir))

    try:
        shutil.rmtree(log_dir)
    except FileNotFoundError:
        print('{} already deleted.'.format(log_dir))
    except PermissionError:
        os.system('sudo rm -rf {}'.format(log_dir))

    try:
        os.remove(cmake_cache_file)
    except FileNotFoundError:
        print('{} already deleted.'.format(cmake_cache_file))

    try:
        shutil.rmtree(cmake_dir)
    except FileNotFoundError:
        print('{} already deleted'.format(cmake_dir))

    try:
        shutil.rmtree(bin_dir)
    except FileNotFoundError:
        print('{} already deleted'.format(bin_dir))

    try:
        os.remove(make_file)
    except FileNotFoundError:
        print('{} already deleted'.format(make_file))


def run_sal():
    print('Starting SAL reference application...')
    set_sal_env()

    if get_selected_profile_name() == common.sal_hw_profile_name and not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)

    sal_executable = os.environ['SAL_HOME'] + '/build/salRefApp'
    os.system('sudo -E LD_LIBRARY_PATH={0}:{1} {2}'.format(
        get_gb_home_absolute() + '/compilation_root',get_sde_home_absolute()+'/install/lib', sal_executable))


def test_sal():
    print("To be integrated")

def take_user_input():
    sal_input = input(
        "Do you want to build(b),clean(c),run(r),test(t) sal, "
        "Enter one or more action chars in appropriate order i.e. cbr?")

    for action_char in sal_input:

        if action_char == 'c':
            clean_sal()
        elif action_char == 'r':
            run_sal()
        elif action_char == 't':
            test_sal()
        elif action_char == 'b':
            build_sal()
        else:
            print("Unrecognised action {}.".format(action_char))

def load_sal_profile():
    print('Installing dependent SWs....')
    load_bf_sde_profile()
    take_user_input()

def just_load_sal():
    """
    When deps of SAL are taken care , Directly execute this file.
    :return:
    """
    read_settings()
    take_user_input()

if __name__ == '__main__':
    just_load_sal()
