import logging
import os

import common
import constants
from bf_sde import set_sde_env_n_load_drivers, load_bf_sde_profile
from common import delete_files, get_env_var, get_gb_lib_home_absolute, \
    execute_cmd, get_from_advance_setting_dict, \
    get_selected_profile_name, set_env_var, get_gb_src_home_absolute, \
    get_abs_path, get_selected_profile_dict, \
    get_sde_home_absolute, append_to_env_var, create_release, get_path_prefix
from drivers import load_and_verify_kernel_modules


def set_sal_runtime_env():
    print("Setting environment for SAL runtime.")
    if not set_sde_env_n_load_drivers():
        return False
    set_env_var(constants.sal_home_env_var_name, get_sal_home_absolute())
    print('SAL_HOME: {}'.format(get_env_var(constants.sal_home_env_var_name)))
    return True


def set_sal_env():
    print("Setting environment for SAL.")
    if not set_sde_env_n_load_drivers():
        return False
    rc = set_env_var(constants.sal_home_env_var_name, get_sal_repo_absolute())
    print('SAL_HOME: {}'.format(get_env_var(constants.sal_home_env_var_name)))
    rc &= set_env_var(constants.pythonpath_env_var_name,
                      get_env_var(constants.sal_home_env_var_name))
    rc &= set_env_var(constants.sde_include_env_var_name,
                      get_env_var(
                          constants.sde_install_env_var_name) + '/include')
    rc &= set_env_var(constants.gb_src_home_env_var_name,
                      get_gb_src_home_absolute())
    rc &= set_env_var(constants.gb_lib_home_env_var_name,
                      get_gb_lib_home_absolute())
    rc &= set_env_var(constants.tp_install_env_var_name,
                      get_tp_install_path_absolute())
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


def get_sal_home_absolute():
    return get_abs_path(get_sal_home_from_config())


def get_sal_repo_absolute():
    return get_abs_path(get_sal_repo_from_config())


def get_tp_install_path_from_settings():
    if not get_from_advance_setting_dict(constants.sal_sw_attr_node,
                                 constants.tp_install_node_name):
        return get_sal_repo_from_config() + '/sal_tp_install/'
    else:
        return get_from_advance_setting_dict(constants.sal_sw_attr_node,
                                     constants.tp_install_node_name)


def get_tp_install_path_absolute():
    return get_abs_path(get_tp_install_path_from_settings())


def get_sal_home_from_config():
    return common.settings_dict. \
        get(constants.sal_sw_attr_node).get(constants.sal_home_node)


def get_sal_repo_from_config():
    return common.advance_settings_dict. \
        get(constants.sal_sw_attr_node).get(constants.sal_repo_node_name)


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


def install_sal_deps():
    os.system('sudo apt install -y libboost-log1.65-dev')
    os.system('python -m pip install grpcio-tools')


def build_sal():
    install_sal_deps()
    print('Building SAL...')
    try:
        # TODO Need to fix this in SAL, to use dedicated boost libs.
        os.system('sudo rm -rf {}'.format('/usr/local/include/boost'))
    except FileNotFoundError:
        pass
    os.chdir(get_env_var(constants.sal_home_env_var_name))
    cmake_cmd = 'cmake '

    cmake_cmd += get_env_var(constants.sal_home_env_var_name)
    print('Executing cmake command {}.'.format(cmake_cmd))

    execute_cmd(cmake_cmd)
    execute_cmd(
        'LD_LIBRARY_PATH={0}/lib:$LD_LIBRARY_PATH make -j -C {1}'.format(
            get_env_var(constants.tp_install_env_var_name),
            get_env_var(constants.sal_home_env_var_name)))

    return True


def prepare_sal_release():
    create_release(get_sal_repo_absolute(),
                   [get_sal_repo_absolute(), '/include/'],
                   [get_sal_repo_absolute(), '/src/include/'],
                   [get_sal_repo_absolute(), '/build'],
                   [get_sal_repo_absolute(), '/lib'],
                   [get_sal_repo_absolute(), '/scripts'],
                   [get_sal_repo_absolute(), '/config'],
                   [get_sal_repo_absolute(), '/proto'],
                   [get_path_prefix(), '/{}/lib'.format(get_tp_install_path_from_settings())],
                   [get_path_prefix(), '/{}/include'.format(get_tp_install_path_from_settings())],
                   [get_path_prefix(), '/{}/bin'.format(get_tp_install_path_from_settings())],
                   [get_path_prefix(), '/{}/share'.format(get_tp_install_path_from_settings())],
                   [get_sal_repo_absolute(), '/README.md'],
                   [get_sal_repo_absolute(), '/test/sal_service_test_BF6064.py'],
                   [get_sal_repo_absolute(), '/test/sal_service_test_BF2556.py'],
                   [get_sal_repo_absolute(), '/test/TestUtil.py'],
                   [get_sal_repo_absolute(), '/sal_services_pb2.py'],
                   [get_sal_repo_absolute(), '/sal_services_pb2_grpc.py'],
                   [get_sal_repo_absolute(), '/sal_services.grpc.pb.cc'],
                   [get_sal_repo_absolute(), '/sal_services.grpc.pb.h'],
                   [get_sal_repo_absolute(), '/sal_services.pb.cc'],
                   [get_sal_repo_absolute(), '/sal_services.pb.h'])
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
    if get_selected_profile_name() == constants.sal_hw_profile_name and not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)
    sal_home=get_env_var(constants.sal_home_env_var_name)
    sal_executable = sal_home + '/build/salRefApp'
    sal_run_cmd = 'sudo -E LD_LIBRARY_PATH={0}:{1}:{2}:{3} {4}'.format(
        sal_home + '/build',
        sal_home + '/lib',
        get_tp_install_path_absolute() + '/lib',
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

sal_3rdparty_path = get_tp_install_path_absolute()


def install_sal_thirdparty_deps():
    print('Installing SAL 3rdparty dependencies.')

    if not os.path.exists(sal_3rdparty_path):
        os.makedirs(sal_3rdparty_path)

    res = installProtobuf()
    append_to_env_var(constants.path_env_var_name,
                      sal_3rdparty_path + '/bin/')
    res &= installgRPC()
    return res


def installProtobuf():
    print('Installing protobuf.')
    protobuf_ver = 'v3.6.1'
    protobuf_dir = '{0}/protobuf{1}/'.format(sal_3rdparty_path, protobuf_ver)
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
    rc = os.system('./configure -q --prefix={}'.format(sal_3rdparty_path))
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


def installgRPC():
    print('Installing gRPC.')
    gRPC_ver = 'v1.17.0'
    gRPC_dir = '{0}/grpc{1}/'.format(sal_3rdparty_path, gRPC_ver)
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

    make_cmd = 'make clean && LD_LIBRARY_PATH={0}/lib/ PKG_CONFIG_PATH={0}/lib/pkgconfig/:$PKG_CONFIG_PATH \
    make -s LDFLAGS=-L{0}/lib prefix={0}'.format(sal_3rdparty_path, 'include/')
    print('Executing CMD: {}'.format(make_cmd))
    rc = os.system(make_cmd)
    if rc != 0:
        print('{} Failed with return code {}'.format(make_cmd, rc))
        return False

    make_install_cmd = 'make -s install prefix={0}'.format(sal_3rdparty_path)
    rc = os.system(make_install_cmd)
    if rc != 0:
        print('{} Failed with return code {}'.format(make_install_cmd, rc))
        return False
    return True


# def installgRPC():
#     print('Installing gRPC.')
#     gRPC_ver = 'v1.17.0'  # This is required version to build PI, check PI's github.
#     gRPC_dir = '{0}/grpc{1}/'.format(sal_thirdparty_path, gRPC_ver)
#     if os.path.exists(gRPC_dir):
#         print('{0} already exists, will rebuild.'.format(gRPC_dir))
#     else:
#         os.system(
#             'git clone https://github.com/google/grpc.git {}'.format(gRPC_dir))
#         os.chdir(gRPC_dir)
#         os.system('git checkout tags/{}'.format(gRPC_ver))
#         os.system('git submodule update --init --recursive')
#
#     os.chdir(gRPC_dir)
#
#     try:
#         os.makedirs(gRPC_dir + '/cmake/build')
#     except FileExistsError:
#         print('cmake directory already exists.')
#     os.chdir('./cmake/build')
#     cmake_cmd = 'cmake ../.. \
#               -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX={}'.format(
#         get_sal_home_absolute() + '/install/')
#     print('Executing gRPC cmake command : {}'.format(cmake_cmd))
#
#     rc = os.system(cmake_cmd)
#     rc = os.system('make -j prefix={}'.format(get_sal_home_absolute() + '/install/'))
#     if rc != 0:
#         return False
#
#     rc = os.system('make prefix={} install'.format(get_sal_home_absolute() + '/install/'))
#     if rc != 0:
#         return False
#
#     # Need to copy grpc_cpp_plugin and libgrpc++.so manually,
#     # Perhaps a bug in grpc_1.17.0 works fine with grpc_1.34.0 .
#     grpc_cpp_plug = get_sal_home_absolute() + \
#                      '/install/bin/grpc_cpp_plugin'
#     lib_grpcpp = get_sal_home_absolute() + \
#                     '/install/lib/libgrpc++.so'
#     shutil.copyfile('grpc_cpp_plugin', grpc_cpp_plug)
#     shutil.copyfile('libgrpc++.so', lib_grpcpp)
#     make_executable(grpc_cpp_plug)
#
#     #ld_cmd = 'sudo ldconfig'
#     #rc = os.system(ld_cmd)
#     # if rc != 0:
#     #     print('{} Failed with return code {}'.format(ld_cmd, rc))
#     #     return False
#     # return True
#     return rc


def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(path, mode)


def execute_user_action(sal_input):
    rc = True

    if 'c' in sal_input:
        rc &= set_sal_env()
        rc &= clean_sal()
    if 'i' in sal_input:
        rc &= install_sal_thirdparty_deps()
    if 'b' in sal_input:
        rc &= set_sal_env()
        rc &= build_sal()
    if 'p' in sal_input:
        rc &= prepare_sal_release()
    if 'r' in sal_input:
        set_sal_runtime_env()
        rc &= run_sal()
    if 't' in sal_input:
        print('Running SAL tests from AOT are currently not supported, '
              'Should run from within SAL package only')
        # rc &= test_sal()
    return rc


def take_user_input():
    sal_input = input(
        "SAL : run(r), [do_nothing(n)], "
        "OR developer's options - "
        "build(b), clean(c), install 3rdParty SWs(i), prepare rel(p) ? ")

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
