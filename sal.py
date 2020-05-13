import os
import shutil

import common
from bf_sde import set_sde_env, load_bf_sde_profile
from common import get_from_setting_dict, \
    set_env_var, pythonpath_env_var_name, \
    get_sde_home_absolute, get_sal_home_absolute, \
    get_env_var, \
    gb_home_env_var_name, get_gb_home_absolute


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
    try:
        os.system('make -C {} clean'.format(os.environ['SAL_HOME']))
        shutil.rmtree(build_dir, ignore_errors=True)
        shutil.rmtree(log_dir, ignore_errors=True)
        os.remove(cmake_cache_file)
        shutil.rmtree(cmake_dir, ignore_errors=True)
        shutil.rmtree(bin_dir, ignore_errors=True)
        os.remove(make_file)
    except FileNotFoundError as e:
        print('SAL is already clean.')


def run_sal():
    print('Starting SAL reference application...')
    set_sal_env()
    sal_executable = os.environ['SAL_HOME'] + '/build/salRefApp'
    os.system('sudo -E {}'.format(sal_executable))


def test_sal():
    print("To be integrated")


def load_sal_profile():
    print('Installing dependent SWs....')
    load_bf_sde_profile()
    sal_input = input(
        "Do you want to [build & run],build(b),clean(c),run(r),test(t) sal?")
    if sal_input in ['clean', 'c']:
        clean_sal()
    elif sal_input in ['run', 'r']:
        run_sal()
    elif sal_input in ['test', 't']:
        test_sal()
    elif sal_input in ['build', 'b']:
        build_sal()
    else:
        build_sal()
        run_sal()
