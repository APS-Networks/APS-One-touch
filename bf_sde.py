import getpass
import os
import shutil
import tarfile
import zipfile
import glob

import common
from common import validate_path_existence, create_symlinks, get_cmd_output, \
    get_path_relative_to_user_home, \
    get_from_setting_dict, get_env_var, set_env_var, get_sde_pkg_name, \
    get_sde_home_absolute, get_sde_dir_name_in_tar, get_bf_sde_profile_name, \
    sde_env_var_name, sde_install_env_var_name, get_selected_profile_name, \
    read_settings
from drivers import load_and_verify_kernel_modules


def build_sde():
    sde_tar = tarfile.open(get_sde_pkg_name())
    sde_home_absolute = get_sde_home_absolute()

    # Deletion is required otherwise moving the directories
    # in further steps might create issues.
    if os.path.exists(sde_home_absolute):
        print("Deleting previous installation at {}.".format(sde_home_absolute))
        os.system('sudo rm -rf {}'.format(sde_home_absolute))

    # Extract tar here i.e. in APS one touch directory
    sde_tar.extractall()
    # In case SDE home is configured in yaml than this directory,
    # If both paths are same following line doesn't cause any problem.
    shutil.move(get_sde_dir_name_in_tar(), sde_home_absolute)
    sde_tar.close()
    os.chdir(sde_home_absolute)
    build_opt = "-up"
    p4studio_build_profile = get_from_setting_dict('BF SDE',
                                                   'p4studio_build_profile')

    if p4studio_build_profile == "":
        build_opt = ""

    sde_install_cmd = "./p4studio_build/p4studio_build.py {} {}".format(
        build_opt,
        p4studio_build_profile)
    print(sde_install_cmd)
    os.system(sde_install_cmd)


def start_bf_switchd():
    # os.chdir(common.dname)
    print('Starting BF switchd.')
    set_sde_env()
    profile_name = get_bf_sde_profile_name()

    if profile_name == common.sde_hw_profile_name and not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)

    if profile_name == common.sde_sim_profile_name:
        # TODO Do something meaningful, Possibly launch tofino model in separate shell,
        # Currently This just an interrupt.
        input('Make sure that tofino-model is running?')

    p4_prog_name = get_from_setting_dict('BF SDE', 'p4_name')

    # LD_LIBRARY_PATH is set for ONLPv2 case, libs in install/lib folder are
    # not found there but this does not cause any harm for Ubuntu case either.
    # set_env('LD_LIBRARY_PATH', "/{0}/install/lib".format(get_env_var('SDE')))
    # print("LD_LIBRARY_PATH : ")
    # os.system("echo $LD_LIBRARY_PATH")

    if not p4_prog_name:
        print("Starting switchd without p4 program")
        start_switchd_cmd = "sudo {0}/install/bin/bf_switchd --install-dir {" \
                            "0}/install --conf-file {" \
                            "0}/pkgsrc/p4-examples/tofino/tofino_skip_p4.conf" \
                            ".in --skip-p4".format(get_env_var('SDE'))
        if profile_name == common.sde_hw_profile_name:
            start_switchd_cmd = "sudo -E {0}/run_switchd.sh -c {0}/pkgsrc/p4-examples/tofino/tofino_skip_p4.conf.in --skip-p4".format(
                get_env_var('SDE'))
    else:
        print("Starting switchd with P4 prog:{}".format(p4_prog_name))
        start_switchd_cmd = 'sudo -E {0} /run_switchd.sh -p {1}'.format(
            get_env_var('SDE'),
            p4_prog_name.replace(".p4", ""))
    username = getpass.getuser()

    if username == "root":
        start_switchd_cmd = start_switchd_cmd.replace("sudo -E", "")
    alloc_dma()
    print("Starting switchd with command : {}".format(start_switchd_cmd))
    os.system(start_switchd_cmd)


def alloc_dma():
    output = get_cmd_output('cat /etc/sysctl.conf')
    if 'vm.nr_hugepages = 128' not in output:
        print('Setting up huge pages...')
        dma_alloc_cmd = 'sudo /{}/pkgsrc/ptf-modules/ptf-utils/dma_setup.sh'.format(
            get_env_var('SDE'))
        os.system(dma_alloc_cmd)

def ask_user_for_building_sde():
    install_sde = input("Do you want to build SDE y/[n]?")
    if not install_sde:
        install_sde = "n"
    if install_sde == "y":
        create_symlinks()
        build_sde()
    else:
        print("You selected not to build SDE.")

def ask_user_for_building_bsp():
    if get_bf_sde_profile_name() == common.sde_hw_profile_name:
        install_bsp = input("Do you want to build BSP y/[n]?")
        if not install_bsp:
            install_bsp = "n"
        if install_bsp == "y":
            install_switch_bsp()
        else:
            print("You selected not to build BSP.")

def ask_user_for_starting_sde():
    start_sde = input("Do you want to start SDE y/[n]?")
    if not start_sde:
        start_sde = "n"
    if start_sde == "y":
        start_bf_switchd()
    else:
        print("You selected not to start SDE.")

def load_bf_sde_profile():

    ask_user_for_building_sde()
    ask_user_for_building_bsp()

    # SDE to be started only in case of SDE profiles
    # Else SDE will be started by SAL or STRATUM
    if get_selected_profile_name() in [common.sde_hw_profile_name,
                                       common.sde_sim_profile_name]:
        ask_user_for_starting_sde()


def set_sde_env():
    sde_home_absolute = get_sde_home_absolute()
    if validate_path_existence(sde_home_absolute, 'SDE'):
        set_env_var(common.sde_env_var_name, sde_home_absolute)
        set_env_var(common.sde_install_env_var_name,
                    get_env_var(common.sde_env_var_name) + '/install')
        print(
            'Environment variables set: \n SDE: {0} \n SDE_INSTALL: {1}'.format(
                get_env_var(common.sde_env_var_name),
                get_env_var(common.sde_install_env_var_name)))
        return True
    return False


def install_switch_bsp():
    set_sde_env()
    bsp_installation_file = get_path_relative_to_user_home(
        get_from_setting_dict('BSP', 'bsp_pkg'))

    if zipfile.is_zipfile(bsp_installation_file):
        print("Installing {}".format(bsp_installation_file))
        zip_ref = zipfile.ZipFile(bsp_installation_file)
        zip_ref.extractall()
        extracted_dir_name = zip_ref.namelist()[0]
        zip_ref.close()
        os.chdir(extracted_dir_name)
        os.environ['BSP'] = os.getcwd()
        print("BSP home directory set to {}".format(os.environ['BSP']))
        os.environ['BSP_INSTALL'] = get_env_var('SDE_INSTALL')
        print(
            "BSP_INSTALL directory set to {}".format(
                os.environ['BSP_INSTALL']))
        for pltfm in glob.glob('./bf-platforms*'):
            os.chdir(pltfm)
        pltfm_dir = os.getcwd()
        os.system("autoreconf && autoconf")
        os.system("chmod +x ./autogen.sh")
        os.system("chmod +x ./configure")
        os.system(
            "./configure --prefix={} --enable-thrift --with-tof-brgup-plat".format(
                os.environ['BSP_INSTALL']))
        os.system("make")
        os.system("sudo make install")
        shutil.rmtree(os.environ['BSP'])
    else:
        print("You choose not to install BSP.")

def just_load_sde():
    read_settings()
    ask_user_for_building_sde()
    ask_user_for_building_bsp()
    ask_user_for_starting_sde()

if __name__ == '__main__':
    just_load_sde()
