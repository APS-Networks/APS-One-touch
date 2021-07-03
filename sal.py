import ipaddress
import os
from threading import Thread

import common
import constants
from bf_sde import set_sde_env_n_load_drivers, load_bf_sde_profile
from common import delete_files, get_env_var, get_gb_lib_home_absolute, \
    execute_cmd, set_env_var, get_gb_src_home_absolute, \
    get_abs_path, \
    append_to_env_var, create_release, get_from_setting_dict, get_p4_prog_name
from constants import path_env_var_name, pythonpath_env_var_name
from drivers import load_and_verify_kernel_modules


def set_sal_runtime_env():
    print("Setting environment for SAL runtime.")
    if not set_sde_env_n_load_drivers():
        return False
    set_env_var(constants.sal_home_env_var_name, get_sal_home_absolute())
    set_env_var(constants.tp_install_env_var_name, get_tp_install_path_absolute())
    os.environ[constants.p4_prog_env_var_name] = get_p4_prog_name()
    print('SAL_HOME: {}'.format(get_env_var(constants.sal_home_env_var_name)))
    print('TP_INSTALL: {}'.format(get_env_var(constants.tp_install_env_var_name)))
    print('P4_PROG: {}'.format(get_env_var(constants.p4_prog_env_var_name)))
    return True


def set_sal_env():
    print("Setting environment for SAL.")
    if not set_sde_env_n_load_drivers():
        return False
    rc = set_env_var(constants.sal_home_env_var_name, get_sal_repo_absolute())
    print('SAL_HOME: {}'.format(get_env_var(constants.sal_home_env_var_name)))
    rc &= set_env_var(constants.sde_include_env_var_name,
                      get_env_var(
                          constants.sde_install_env_var_name) + '/include')
    rc &= set_env_var(constants.gb_src_home_env_var_name,
                      get_gb_src_home_absolute())
    rc &= set_env_var(constants.gb_lib_home_env_var_name,
                      get_gb_lib_home_absolute())
    rc &= set_env_var(constants.tp_install_env_var_name,
                      get_tp_install_path_absolute())
    print('SAL_HOME: %s \
    \n SDE: %s \
    \n SDE_INSTALL: %s \
    \n SDE_INCLUDE: %s \
    \n GB_SRC_HOME: %s \
    \n GB_LIB_HOME: %s \
    \n TP_INSTALL: %s' %
          (get_env_var(constants.sal_home_env_var_name),
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
    if not get_from_setting_dict(constants.sal_sw_attr_node,
                                 constants.tp_install_node_name):
        return get_sal_home_from_config() + '/sal_tp_install/'
    else:
        return get_from_setting_dict(constants.sal_sw_attr_node,
                                     constants.tp_install_node_name)


def get_tp_install_path_absolute():
    return get_abs_path(get_tp_install_path_from_settings())


def get_sal_home_from_config():
    return common.settings_dict. \
        get(constants.sal_sw_attr_node).get(constants.sal_home_node)


def get_sal_repo_from_config():
    return common.advance_settings_dict. \
        get(constants.sal_sw_attr_node).get(constants.sal_repo_node_name)


def install_sal_build_deps():
    os.system('python3 -m pip install grpcio-tools')
    os.system('sudo apt install g++-8 gcc-8')
    return True


def build_sal():
    print('Building SAL...')

    cmake_cmd = 'cmake '
    cmake_cmd += ' -B ' + get_env_var(constants.sal_home_env_var_name)
    cmake_cmd += ' -S ' + get_env_var(constants.sal_home_env_var_name)

    print('Executing cmake command {}.'.format(cmake_cmd))

    execute_cmd(cmake_cmd)
    execute_cmd(
        'LD_LIBRARY_PATH={0}/lib:$LD_LIBRARY_PATH make -C {1}'.format(
            get_env_var(constants.tp_install_env_var_name),
            get_env_var(constants.sal_home_env_var_name)))

    return True


def prepare_sal_release():
    files_to_copy = [
        [get_sal_repo_absolute(), '/include/'],
        [get_sal_repo_absolute(), '/src/include/'],
        [get_sal_repo_absolute(), '/build'],
        [get_sal_repo_absolute(), '/lib'],
        [get_sal_repo_absolute(), '/scripts'],
        [get_sal_repo_absolute(), '/config'],
        [get_sal_repo_absolute(), '/proto'],
        [get_sal_repo_absolute(), '/README.md'],
        [get_sal_repo_absolute(), '/test/sal_service_test_BF6064.py'],
        [get_sal_repo_absolute(), '/test/sal_service_test_BF2556.py'],
        [get_sal_repo_absolute(), '/test/TestUtil.py'],
        [get_sal_repo_absolute(), '/sal_services_pb2.py'],
        [get_sal_repo_absolute(), '/sal_services_pb2_grpc.py'],
        [get_sal_repo_absolute(), '/sal_services.grpc.pb.cc'],
        [get_sal_repo_absolute(), '/sal_services.grpc.pb.h'],
        [get_sal_repo_absolute(), '/sal_services.pb.cc'],
        [get_sal_repo_absolute(), '/sal_services.pb.h']
    ]

    package_input = input("Package 3rdParty [y]/n:")
    if not package_input:
        package_input = 'y'
    if package_input == 'y':
        files_to_copy.append([get_sal_repo_absolute(), '/{}/lib'.
                              format(sal_3rdparty_build_dir)])
        files_to_copy.append([get_sal_repo_absolute(), '/{}/include'.
                              format(sal_3rdparty_build_dir)])
        files_to_copy.append([get_sal_repo_absolute(), '/{}/bin'.
                              format(sal_3rdparty_build_dir)])
        files_to_copy.append([get_sal_repo_absolute(), '/{}/share'.
                              format(sal_3rdparty_build_dir)])
    create_release(get_sal_repo_absolute(), files_to_copy)

    return True


def clean_sal():
    print('Cleaning SAL...')
    to_delete = [get_env_var(constants.sal_home_env_var_name) + f for f in
                 ['/lib', '/bin', '/build', '/logs/', '/CMakeCache.txt',
                  '/Makefile',
                  '/CMakeFiles', '/cmake-build-debug']]
    execute_cmd(
        'make -C {} clean'.
        format(get_env_var(constants.sal_home_env_var_name)))

    for file in to_delete:
        print('Deteling {}'.format(file))
        delete_files(file)
    return True


def run_sal(debug):
    print('Starting SAL reference application...')
    if not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)
    sal_home = get_env_var(constants.sal_home_env_var_name)
    sal_executable = sal_home + '/build/salRefApp'
    sal_run_cmd = 'sudo -E LD_LIBRARY_PATH={0}:{1}:{2}:{3}:{4} {6} {5}'.format(
        sal_home + '/build',
        sal_home + '/lib',
        get_env_var(constants.tp_install_env_var_name) + '/lib',
        get_env_var(constants.sal_home_env_var_name) + '/install/lib',
        get_env_var(constants.sde_install_env_var_name) + '/lib', sal_executable,
        'gdb' if debug else '')
    print('Running SAL with command: {}'.format(sal_run_cmd))
    execute_cmd(sal_run_cmd)
    return True


def get_dut_ips():
    return get_from_setting_dict(constants.sal_sw_attr_node, constants.dut_ips_node_name)


def is_valid_ip(ipaddr):
    try:
        ipaddress.ip_address(ipaddr)
        return True
    except ValueError:
        print('address/netmask is invalid : %s' % ipaddr)
        return False


def set_sal_test_env():
    set_env_var(constants.sal_home_env_var_name, get_sal_home_absolute())
    append_to_env_var(pythonpath_env_var_name, get_env_var(constants.sal_home_env_var_name))
    append_to_env_var(pythonpath_env_var_name, get_env_var(constants.sal_home_env_var_name) + "/test")
    print("%s = %s" % (pythonpath_env_var_name, get_env_var(pythonpath_env_var_name)))


def execute_test_cmd(ip, sal_grpc_port):
    test_cmd = 'python3 %s/test/SAL_Tests.py %s %s' % \
               (get_env_var(constants.sal_home_env_var_name), ip, sal_grpc_port)
    os.system(test_cmd)


def install_sal_test_deps():
    os.system('pip3 install --upgrade pip')
    os.system('pip3 install future paramiko grpcio-tools html-testRunner setuptools_rust')
    return True


def get_sal_ip_port_dict():
    ip_port_dict = {}
    dut_ips = get_dut_ips()
    if dut_ips is not None:
        for ip in dut_ips:
            ip_port = ip.split(':')
            try:
                dev_ip = ip_port[0]
                sal_grpc_port = ip_port[1]
                if not is_valid_ip(dev_ip) and not sal_grpc_port:
                    raise ValueError
                elif dev_ip not in ip_port_dict:
                    ip_port_dict[dev_ip] = sal_grpc_port
            except (IndexError, ValueError) as e:
                print("ERROR: Invalid DUT_IP or gRPC Port provided for connecting to SAL. : %s" % e)
    print("Devices to be tested %s" % ip_port_dict)
    return ip_port_dict


def execute_sal_tests():
    print("Executing tests from %s." % get_env_var(constants.sal_home_env_var_name))

    for dev_ip, sal_grpc_port in get_sal_ip_port_dict().items():
        t = Thread(target=execute_test_cmd, name='SAL Tests thread for device %s ' % dev_ip,
                   args=(dev_ip, sal_grpc_port,))
        print("Starting %s" % t.name)
        t.start()
    return True


# Dependencies will be built inside local repository at following fixed path.
# To run SAL path for 3rdParty path 'tp_install' in settings.yaml is used,
# Which may or may not be same as following 3rdParty build path.
sal_3rdparty_build_dir = '/sal_tp_install'
sal_3rdparty_build_path = get_sal_repo_absolute() + sal_3rdparty_build_dir


def install_sal_thirdparty_deps():
    print('Installing SAL 3rdparty dependencies.')

    if not os.path.exists(sal_3rdparty_build_path):
        os.makedirs(sal_3rdparty_build_path)

    i = input('Install boost y/[n] ?')
    if not i or i not in ['y', 'n']:
        i = 'n'
    if i == 'y' and not install_boost():
        return False

    i = input('Install protobuf y/[n] ?')
    if not i or i not in ['y', 'n']:
        i = 'n'
    if i == 'y' and not install_protobuf():
        return False

    append_to_env_var(constants.path_env_var_name,
                      sal_3rdparty_build_path + '/bin/')
    print(get_env_var(path_env_var_name))

    i = input('Install gRPC y/[n] ?')
    if not i or i not in ['y', 'n']:
        i = 'n'
    if i == 'y' and not install_grpc():
        return False
    return True


def install_protobuf():
    print('Installing protobuf.')
    protobuf_ver = 'v3.6.1'
    protobuf_dir = '{0}/protobuf{1}/'.format(sal_3rdparty_build_path, protobuf_ver)
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
    rc = os.system('./configure -q --prefix={}'.format(sal_3rdparty_build_path))
    if rc != 0:
        return False
    rc = os.system('make -s')
    if rc != 0:
        return False
    # os.system('make check')
    rc = os.system('make -s -j install')
    if rc != 0:
        return False
    rc = os.system('sudo ldconfig')
    if rc != 0:
        return False
    return True


def install_grpc():
    print('Installing gRPC.')
    grpc_ver = 'v1.17.0'
    grpc_dir = '{0}/grpc{1}/'.format(sal_3rdparty_build_path, grpc_ver)
    if os.path.exists(grpc_dir):
        print('{0} already exists, will rebuild.'.format(grpc_dir))
    else:
        os.system(
            'git clone https://github.com/google/grpc.git {}'.format(grpc_dir))
        os.chdir(grpc_dir)
        os.system('git checkout tags/{}'.format(grpc_ver))
        os.system('git submodule update --init --recursive')

    os.chdir(grpc_dir)
    make_cmd = 'make clean && LD_LIBRARY_PATH={0}/lib/ PKG_CONFIG_PATH={0}/lib/pkgconfig/:$PKG_CONFIG_PATH \
    make -s -I{0} LDFLAGS=-L{0}/lib prefix={0}'.format(sal_3rdparty_build_path, 'include/')
    print('Executing CMD: {}'.format(make_cmd))
    rc = os.system(make_cmd)
    if rc != 0:
        print('{} Failed with return code {}'.format(make_cmd, rc))
        return False

    make_install_cmd = 'make -s -j install prefix={0}'.format(sal_3rdparty_build_path)
    rc = os.system(make_install_cmd)
    if rc != 0:
        print('{} Failed with return code {}'.format(make_install_cmd, rc))
        return False
    return True


def install_boost():
    print('Installing Boost.')
    boost_ver = '1_67_0'
    boost_dir = '{0}/boost_{1}/'.format(sal_3rdparty_build_path, boost_ver)
    boost_arch_name = 'boost_{}.tar.bz2'.format(boost_ver)

    if os.path.exists(boost_dir):
        print('{0} already exists, will rebuild.'.format(boost_dir))
    else:
        os.system('wget http://downloads.sourceforge.net/project/boost/boost/{0}/{1} -P {2}'.
                  format(boost_ver.replace('_', '.'), boost_arch_name, sal_3rdparty_build_path))

    rc = os.system('tar -xvf {0} -C {1}'.
                   format(sal_3rdparty_build_path + '/' + boost_arch_name, sal_3rdparty_build_path))
    os.chdir(boost_dir)
    print('./bootstrap.sh --prefix={}'.format(sal_3rdparty_build_path))
    rc &= os.system('./bootstrap.sh --prefix={}'.format(sal_3rdparty_build_path))
    rc &= os.system('./b2 -j')
    rc &= os.system('./b2 --with-system --with-log --with-program_options install')
    rc &= os.system('sudo ldconfig')
    rc &= os.system('chmod -R a+rwx {}'.format(boost_dir))
    if rc != 0:
        print('Boost build failed !')
        return False

    return True


def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(path, mode)


def execute_user_action(sal_input):
    rc = True

    if 'c' in sal_input:
        set_env_var(constants.sal_home_env_var_name, get_sal_home_absolute())
        rc &= clean_sal()
    if 'i' in sal_input:
        rc &= install_sal_thirdparty_deps()
    if 'b' in sal_input:
        rc &= install_sal_build_deps()
        rc &= set_sal_env()
        rc &= build_sal()
    if 'p' in sal_input:
        rc &= prepare_sal_release()
    if 'r' in sal_input or 'd' in sal_input:
        set_sal_runtime_env()
        rc &= run_sal('d' in sal_input)
    if 't' in sal_input:
        set_sal_test_env()
        install_sal_test_deps()
        rc &= execute_sal_tests()
    return rc


def take_user_input():
    sal_input = input(
        "SAL : run(r), execute_tests(t), [do_nothing(n)]? ")
        # "OR developer's options - "
        # "build(b), clean(c), debug(d),  "
        # "install 3rdParty SWs(i), "
        # "prepare rel(p) ? ")

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
