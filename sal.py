import logging
import os
import shutil

import common
import constants
from bf_sde import set_sde_env_n_load_drivers, load_bf_sde_profile
from common import delete_files, get_env_var, get_gb_lib_home_absolute, \
    get_gb_src_home_absolute, get_path_relative_to_user_home, \
    get_sde_home_absolute, get_selected_profile_dict, get_selected_profile_name,\
    set_env_var, \
    append_to_env_var, get_from_setting_dict, \
    execute_cmd

get_gb_src_home_absolute, get_path_relative_to_user_home, get_sde_home_absolute, get_selected_profile_dict,
get_selected_profile_name, set_env_var
from drivers import load_and_verify_kernel_modules

sal_thirdparty_path = ''


def set_sal_env():
    print("Setting environment for SAL.")
    if not set_sde_env_n_load_drivers():
        return False
        exit()
    rc = set_env_var(constants.sal_home_env_var_name, get_sal_home_absolute())
    rc &= set_env_var(constants.pythonpath_env_var_name,
                      get_sal_home_absolute())
    rc &= set_env_var(constants.sde_include_env_var_name,
                      get_env_var(
                          constants.sde_install_env_var_name) + '/include')
    rc &= set_env_var(constants.gb_src_home_env_var_name,
                      get_gb_src_home_absolute())
    rc &= set_env_var(constants.gb_lib_home_env_var_name,
                      get_gb_lib_home_absolute())
    # rc &= set_env_var(constants.sal_install_env_var_name,
    #                   get_sal_home_absolute() + '/install/')
    if get_from_setting_dict(constants.sal_sw_attr_node,
                             constants.build_third_party_node):
        if get_from_setting_dict(constants.sde_details_node,
                                 constants.tp_install_node_name) is None:
            rc &= set_env_var(constants.tp_install_env_var_name,
                              get_sal_home_absolute() + '/install/')
        else:
            rc &= set_env_var(constants.tp_install_env_var_name,
                              get_from_setting_dict(constants.sde_details_node,
                                                    get_tp_install_path_absolute()))
    else:
        rc &= set_env_var(constants.tp_install_env_var_name,
                          get_env_var(constants.sde_install_env_var_name))

    print('SAL_HOME: {0} \
    \n PYTHONPATH: {1} \
    \n SDE: {2} \
    \n SDE_INSTALL: {3} \
    \n SDE_INCLUDE: {4} \
    \n GB_SRC_HOME: {5} \
    \n GB_LIB_HOME: {6} \
    \n TP_INSTALL: {7}'.format(
        get_env_var(constants.sal_home_env_var_name),
        get_env_var(constants.pythonpath_env_var_name),
        get_env_var(constants.sde_env_var_name),
        get_env_var(constants.sde_install_env_var_name),
        get_env_var(constants.sde_include_env_var_name),
        get_env_var(constants.gb_src_home_env_var_name),
        get_env_var(constants.gb_lib_home_env_var_name),
        get_env_var(constants.tp_install_env_var_name)))
    return rc


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


def get_tp_install_path_absolute():
    return get_path_relative_to_user_home(get_from_setting_dict(constants.sde_details_node,
                                                    constants.tp_install_node_name))

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

    execute_cmd(cmake_cmd)
    execute_cmd('LD_LIBRARY_PATH={0}/lib:$LD_LIBRARY_PATH make -C {1}'.format(
        get_env_var(constants.tp_install_env_var_name),
        get_env_var(constants.sal_home_env_var_name)))

    return True


sal_rel_dir = common.release_dir + '/sal'


def prepare_sal_release():
    try:
        os.mkdir(sal_rel_dir)
        print('SAL release directory {} created.'.format(sal_rel_dir))
    except FileExistsError:
        print('SAL Release directory {} already exists, recreated.'.format(
            sal_rel_dir))
        delete_files(sal_rel_dir)
        os.mkdir(sal_rel_dir)

    shutil.copytree(get_env_var(constants.sal_home_env_var_name) + '/include/',
                    sal_rel_dir + '/include')
    shutil.copytree(
        get_env_var(constants.sal_home_env_var_name) + '/src/include/',
        sal_rel_dir + '/src/include')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name) + '/build',
                    sal_rel_dir + '/build')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name) + '/lib',
                    sal_rel_dir + '/lib')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name) + '/scripts',
                    sal_rel_dir + '/scripts')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name) + '/config',
                    sal_rel_dir + '/config')
    shutil.copytree(get_env_var(constants.sal_home_env_var_name) + '/proto',
                    sal_rel_dir + '/proto')
    if get_from_setting_dict(constants.sal_sw_attr_node,
                             constants.build_third_party_node):
        shutil.copytree(
            get_env_var(constants.tp_install_env_var_name) + '/lib',
            sal_rel_dir + '/install/lib')
        shutil.copytree(
            get_env_var(constants.tp_install_env_var_name) + '/include',
            sal_rel_dir + '/install/include')
        shutil.copytree(
            get_env_var(constants.tp_install_env_var_name) + '/bin',
            sal_rel_dir + '/install/bin')
        shutil.copytree(
            get_env_var(constants.tp_install_env_var_name) + '/share',
            sal_rel_dir + '/install/share')

    os.mkdir(sal_rel_dir + '/test')
    shutil.copyfile(get_env_var(constants.sal_home_env_var_name) + '/README.md',
                    sal_rel_dir + '/README.md')
    shutil.copyfile(get_env_var(
        constants.sal_home_env_var_name) + '/test/sal_service_test_BF6064.py',
                    sal_rel_dir + '/test/sal_service_test_BF6064.py')
    shutil.copyfile(get_env_var(
        constants.sal_home_env_var_name) + '/test/sal_service_test_BF2556.py',
                    sal_rel_dir + '/test/sal_service_test_BF2556.py')
    shutil.copyfile(
        get_env_var(constants.sal_home_env_var_name) + '/test/TestUtil.py',
        sal_rel_dir + '/test/TestUtil.py')
    shutil.copyfile(
        get_env_var(constants.sal_home_env_var_name) + '/sal_services_pb2.py',
        sal_rel_dir + '/sal_services_pb2.py')
    shutil.copyfile(get_env_var(
        constants.sal_home_env_var_name) + '/sal_services_pb2_grpc.py',
                    sal_rel_dir + '/sal_services_pb2_grpc.py')
    shutil.copyfile(
        get_env_var(constants.sal_home_env_var_name) + '/sal_services_pb2.py',
        sal_rel_dir + '/sal_services.grpc.pb.cc')
    shutil.copyfile(get_env_var(
        constants.sal_home_env_var_name) + '/sal_services_pb2_grpc.py',
                    sal_rel_dir + '/sal_services.grpc.pb.h')
    shutil.copyfile(get_env_var(
        constants.sal_home_env_var_name) + '/sal_services_pb2_grpc.py',
                    sal_rel_dir + '/sal_services.pb.cc')
    shutil.copyfile(get_env_var(
        constants.sal_home_env_var_name) + '/sal_services_pb2_grpc.py',
                    sal_rel_dir + '/sal_services.pb.h')

    print('SAL release is available at {}'.format(sal_rel_dir))
    return True


def clean_sal():
    print('Cleaning SAL...')

    to_delete = [get_env_var(constants.sal_home_env_var_name) + f for f in
                 ['/lib', '/bin', '/build', '/logs/', '/CMakeCache.txt',
                  '/Makefile',
                  '/CMakeFiles', '/cmake-build-debug']]
    execute_cmd(
        'make -C {} clean'.format(get_env_var(constants.sal_home_env_var_name)))

    for file in to_delete:
        print('Deteling {}'.format(file))
        delete_files(file)
    return True


def run_sal():
    print('Starting SAL reference application...')
    set_sal_runtime_env()
    if get_selected_profile_name() == constants.sal_hw_profile_name and not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)

    sal_executable = sal_rel_dir + '/build/salRefApp'
    sal_run_cmd = 'sudo -E LD_LIBRARY_PATH={0}:{1}:{2}:{3} {4}'.format(
        sal_rel_dir + '/build',
        sal_rel_dir + '/lib',
        get_env_var(constants.sal_home_env_var_name) + '/install/lib',
        get_sde_home_absolute() + '/install/lib', sal_executable)
    print('Running SAL with command: {}'.format(sal_run_cmd))
    execute_cmd(sal_run_cmd)
    return True

# Currently SAL has to be tested from within SAL package package
# def test_sal():
#     # First kill salRefApp in case it is already running
#     os.system("sudo pkill -9 {}".format('salRefApp'))
#
#     # Run sal in a separate thread.
#     t = Thread(target=run_sal, name='Run SAL')
#     t.daemon = True
#     t.start()
#     set_sal_runtime_env()
#     print(get_env_var(constants.sal_home_env_var_name))
#     sys.path.append(get_env_var(constants.sal_home_env_var_name))
#     sys.path.append(get_env_var(constants.sal_home_env_var_name) + "/test/")
#
#     try:
#         host = sys.argv[1]
#         ssh_user = sys.argv[2]
#         ssh_password = sys.argv[3]
#         os.system('python3 {0}/test/sal_service_test_BF2556.py {1} {2} {3}'.
#                   format(get_env_var(constants.sal_home_env_var_name),
#                          host, ssh_user, ssh_password))
#
#     except IndexError:
#         print(
#             'While executing tests provide device IP ssh user and pssword '
#             'separated with space to the script.')
#     finally:
#         os.system("sudo pkill -9 {}".format('salRefApp'))
#     return True


def install_sal_thirdparty_deps():
    print('Installing SAL thirdparty dependencies.')
    global sal_thirdparty_path
    sal_thirdparty_path = get_sal_home_absolute() + '/install/thirdparty/'

    if not os.path.exists(sal_thirdparty_path):
        os.makedirs(sal_thirdparty_path)

    res = installProtobuf()
    append_to_env_var(constants.path_env_var_name,
                      get_sal_home_absolute() + '/install/bin/')
    res &= installgRPC()
    res &= installPI()
    return res


def installProtobuf():
    print('Installing protobuf.')
    protobuf_ver = 'v3.6.1'
    protobuf_dir = '{0}/protobuf{1}/'.format(sal_thirdparty_path, protobuf_ver)
    if os.path.exists(protobuf_dir):
        print('{0} already exists, will rebuild.'.format(protobuf_dir))
    else:
        os.system(
            'git clone https://github.com/protocolbuffers/protobuf.git {}'.format(
                protobuf_dir))
        os.chdir(protobuf_dir)
        os.system('git checkout tags/{}'.format(protobuf_ver))

    os.chdir(protobuf_dir)
    os.system('./autogen.sh')
    rc = os.system('./configure -q --prefix={}'.format(
        get_sal_home_absolute() + '/install/'))
    if rc != 0:
        return False
    rc = os.system('make -s')
    if rc != 0:
        return False
    # os.system('make check')
    rc = os.system('make -s install')
    if rc != 0:
        return False
    rc = os.system('sudo ldconfig')
    if rc != 0:
        return False
    return True
    # os.system('sudo pip install protobuf=={}'.format(protobuf_ver))


def installgRPC():
    print('Installing gRPC.')
    gRPC_ver = 'v1.17.0'
    gRPC_dir = '{0}/grpc{1}/'.format(sal_thirdparty_path, gRPC_ver)
    if os.path.exists(gRPC_dir):
        print('{0} already exists, will rebuild.'.format(gRPC_dir))
    else:
        os.system(
            'git clone https://github.com/google/grpc.git {}'.format(gRPC_dir))
        os.chdir(gRPC_dir)
        os.system('git checkout tags/{}'.format(gRPC_ver))
        os.system('git submodule update --init --recursive')

    os.chdir(gRPC_dir)

    #         os.makedirs(gRPC_dir+'/cmake/build')
    #         cmake_cmd='cmake ../.. -DgRPC_INSTALL=ON \
    #                   -DgRPC_BUILD_TESTS=OFF \
    #                   -DCMAKE_INSTALL_PREFIX={}'.format(get_sal_home_absolute()+'/install/')
    #         print('Executing gRPC cmake command : '.format(cmake_cmd))
    #         rc=os.system(cmake_cmd)

    make_cmd = 'LD_LIBRARY_PATH={0}/lib/ PKG_CONFIG_PATH={0}/lib/pkgconfig/:$PKG_CONFIG_PATH \
    make -s LDFLAGS=-L{0}/lib prefix={0}'.format(
        get_sal_home_absolute() + '/install/')
    print('Executing CMD: {}'.format(make_cmd))
    rc = os.system(make_cmd)
    if rc != 0:
        print('{} Failed with return code {}'.format(make_cmd, rc))
        return False

    make_install_cmd = 'make -s install prefix={0}'.format(
        get_sal_home_absolute() + '/install/')
    rc = os.system(make_install_cmd)
    if rc != 0:
        print('{} Failed with return code {}'.format(make_install_cmd, rc))
        return False

    ld_cmd = 'sudo ldconfig'
    rc = os.system(ld_cmd)
    if rc != 0:
        print('{} Failed with return code {}'.format(ld_cmd, rc))
        return False
    return True


def installPI():
    print('Installing PI.')
    pi_dir = '{0}/PI/'.format(sal_thirdparty_path)
    if os.path.exists(pi_dir):
        print('{0} already exists, will rebuild.'.format(pi_dir))
    else:
        os.system(
            'git clone https://github.com/p4lang/PI.git {}'.format(pi_dir))
        # os.system('git checkout 41358da0ff32c94fa13179b9cee0ab597c9ccbcc')
        os.chdir(pi_dir)
        os.system('git submodule update --init --recursive')

    os.chdir(pi_dir)

    os.system('./autogen.sh')
    config_cmd = 'PKG_CONFIG_PATH={0}/lib/pkgconfig:$PKG_CONFIG_PATH \
    ./configure -q CFLAGS=-Wno-error CPPFLAGS=-I{0}/include LDFLAGS=-L{0}/lib \
     --prefix={0} --with-proto=yes'.format(
        get_sal_home_absolute() + '/install/')
    print('Executing PI config command : {}'.format(config_cmd))
    rc = os.system(config_cmd)
    if rc != 0:
        print('{} Failed with return code {}'.format(config_cmd, rc))
        return False
    rc = os.system('LD_LIBRARY_PATH={0}/lib/ make -s LDFLAGS=-L{0}/lib'.
                   format(get_sal_home_absolute() + '/install/'))
    if rc != 0:
        return False
    # rc=os.system('make -s install prefix={}'.format(get_sal_home_absolute()+'/install/'))
    rc = os.system('make -s install')
    if rc != 0:
        return False
    return True


def execute_user_action(sal_input):
    rc = True
    for action_char in sal_input:
        if action_char == 'c':
            rc &= set_sal_env()
            rc &= clean_sal()
        elif action_char == 'r':
            rc &= run_sal()
        elif action_char == 't':
            print('Running SAL tests from AOT are currently not supported, '
                  'Should run from within SAL package only')
            #rc &= test_sal()
        elif action_char == 'b':
            rc &= set_sal_env()
            rc &= build_sal()
            rc &= prepare_sal_release()
        elif action_char == 'i':
            if get_from_setting_dict(constants.sal_sw_attr_node,
                                     constants.build_third_party_node):
                rc &= install_sal_thirdparty_deps()
            else:
                print(
                    'But choose not to build thirdparty SW. Check settings.yaml')
        else:
            print(
                "Invalid action {0} or action doesn't fit with selected profile {1}.".format(
                    action_char, get_selected_profile_name()))
            return False
    return rc


def take_user_input():
    sal_input = input(
        "SAL : run(r), [do_nothing(n)] ? ")

    if 'n' in sal_input or not sal_input:
        # In case user give nasty input like cbrn
        # User meant do nothing in such cases
        return

    execute_user_action(sal_input)


def load_sal_profile():
    load_bf_sde_profile()
    take_user_input()


def just_load_sal():
    """
    When deps of SAL are taken care already, Directly execute this file.
    :return:
    """
    take_user_input()


if __name__ == '__main__':
    just_load_sal()
