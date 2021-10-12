import getpass
import os
import shutil
import tarfile
import zipfile
from pathlib import Path

import constants
from common import create_symlinks, execute_cmd_n_get_output, get_env_var, \
    get_from_setting_dict, \
    get_sde_dir_name_in_tar, get_sde_home_absolute, get_sde_pkg_abs_path, \
    set_env_var, validate_path_existence, \
    append_to_env_var, \
    dname, get_switch_model, execute_cmd, get_ref_bsp_abs_path, \
    get_aps_bsp_pkg_abs_path, execute_cmd_n_get_output_2, get_abs_path, \
    get_from_advance_setting_dict, create_release, get_p4_prog_name, do_basic_path_validation
from constants import stratum_profile, p4_prog_env_var_name
from drivers import load_and_verify_kernel_modules


def get_sde_build_flags():
    return get_from_setting_dict(constants.sde_details_node, constants.sde_build_flags_node)


def get_p4_studio_build_profile_name():
    return get_from_setting_dict('BF SDE', 'p4studio_build_profile')


def install_sde_deps():
    os.system('sudo apt -y install python')


def build_sde():
    #install_sde_deps()
    sde_tar = tarfile.open(get_sde_pkg_abs_path())
    sde_home_absolute = get_sde_home_absolute()
    sde_build_flags = get_sde_build_flags()

    # Deletion is required otherwise moving the directories
    # in further steps might create issues.
    # And delete only when user have opted for not to resume build
    # if sde_build_flags is not None and '-rb' not in sde_build_flags \
    #         and '-bm' not in sde_build_flags:
    try:
        print("Deleting previous installation at {}.".format(
            sde_home_absolute))
        os.system('sudo rm -rf {}'.format(sde_home_absolute))
    except FileNotFoundError:
        print('{} already deleted.'.format(sde_home_absolute))

    # Extract tar here i.e. in APS one touch directory
    sde_tar.extractall()
    # In case SDE home is configured in yaml other than this directory,
    # If both paths are same following line doesn't cause any problem.
    if not os.path.exists(sde_home_absolute):
        shutil.move(get_sde_dir_name_in_tar(), sde_home_absolute)
    sde_tar.close()
    os.chdir(sde_home_absolute)
    p4studio_build_profile = get_abs_path(get_p4_studio_build_profile_name())

    sde_install_cmd = "{0}/p4studio/p4studio profile apply {1}".format(
        sde_home_absolute,
        p4studio_build_profile)

    os.environ[
        constants.path_env_var_name] += os.pathsep + sde_home_absolute + '/install/bin/'
    print('Building sde with command {}'.format(sde_install_cmd))
    os.system(sde_install_cmd)
    return True


def start_bf_switchd():
    # os.chdir(common.dname)
    print('Starting BF switchd.')
    set_sde_env_n_load_drivers()

    p4_prog_name = get_env_var(p4_prog_env_var_name)

    # LD_LIBRARY_PATH is set for ONLPv2 case, libs in install/lib folder are
    # not found there but this does not cause any harm for Ubuntu case either.
    # set_env('LD_LIBRARY_PATH', "/{0}/install/lib".format(get_env_var('SDE')))
    # print("LD_LIBRARY_PATH : ")
    # os.system("echo $LD_LIBRARY_PATH")

    if not p4_prog_name:
        print("Starting switchd without p4 program")
        start_switchd_cmd = "sudo -E {0}/run_switchd.sh -c {0}/pkgsrc/p4-examples/tofino/tofino_skip_p4.conf.in " \
                            "--skip-p4".format(get_env_var('SDE'))
    else:
        print("Starting switchd with P4 prog:{}".format(p4_prog_name))
        start_switchd_cmd = 'sudo -E {0}/run_switchd.sh -p {1}'.format(
            get_env_var('SDE'),
            p4_prog_name.replace(".p4", ""))
    username = getpass.getuser()

    if username == "root":
        start_switchd_cmd = start_switchd_cmd.replace("sudo -E", "")
    alloc_dma()
    print("Starting switchd with command : {}".format(start_switchd_cmd))
    os.system(start_switchd_cmd)


def alloc_dma():
    output = execute_cmd_n_get_output('cat /etc/sysctl.conf')
    if 'vm.nr_hugepages = 128' not in output:
        print('Setting up huge pages...')
        dma_alloc_cmd = 'sudo /{}/pkgsrc/ptf-modules/ptf-utils/dma_setup.sh'.format(
            get_env_var('SDE'))
        os.system(dma_alloc_cmd)


def ask_user_for_building_sde():
    install_sde = input("SDE : build y/[n]?")
    if not install_sde:
        install_sde = "n"
    if install_sde == "y":
        create_symlinks()
        build_sde()


def get_diff_file_name():
    return '{}.diff'.format(get_switch_model()).lower()


def get_bsp_repo_abs_path():
    path_from_adv_setting = get_from_advance_setting_dict(
        constants.BSP_node, constants.bsp_repo_node_name)
    if path_from_adv_setting is None:
        return get_default_bsp_repo_path()
    else:
        return get_abs_path(path_from_adv_setting)


def prepare_bsp_pkg():
    bsp_repo_abs = get_bsp_repo_abs_path()
    earliest_commit_hash = execute_cmd_n_get_output_2(
        'git --git-dir {0}/.git rev-list --max-parents=0 HEAD'.format(
            bsp_repo_abs))
    latest_commit_hash = execute_cmd_n_get_output_2(
        'git --git-dir {0}/.git rev-parse HEAD'.format(bsp_repo_abs))
    os.chdir(bsp_repo_abs)
    execute_cmd_n_get_output_2(
        'git --git-dir {0}/.git diff {1} {2} -- '
        '\':!./platforms/apsn/\' '
        '\':!.idea/\' '
        '\':!.gitignore\' '
        '\':!autom4te.cache\' '
        '\':!*Makefile.in\' '
        '> {3}'.format(bsp_repo_abs, earliest_commit_hash, latest_commit_hash,
                       bsp_repo_abs + '/' + get_diff_file_name()))
    create_release(bsp_repo_abs, [[bsp_repo_abs, get_diff_file_name()],
                                  [bsp_repo_abs, '/platforms/apsn/']])


def ask_user_for_building_bsp():
    in_put = input("BSP : build y/[n]? ")
    # "OR developer's option- packaging(p)?")
    if not in_put:
        in_put = "n"
    # Order is important, if 'p' and 'y' both oprions are given
    # Then first package then build
    if "p" in in_put:
        prepare_bsp_pkg()
    if "y" in in_put:
        install_switch_bsp()


def ask_user_for_starting_sde():
    start_sde = input("SDE : start y/[n]?")
    if not start_sde:
        start_sde = "n"
    if start_sde == "y":
        start_bf_switchd()
    else:
        print("You selected not to start SDE.")


def load_bf_sde_profile():
    ask_user_for_building_sde()
    ask_user_for_building_bsp()
    prepare_sde_release()
    ask_user_for_starting_sde()


def prepare_sde_release():
    # TODO prepare precompiled binaries from SDE, to avoid the need for
    #  building SDE.
    pass


def set_sde_env():
    print("Setting environment for BF_SDE.")
    sde_home_absolute = get_sde_home_absolute()
    if validate_path_existence(sde_home_absolute, 'SDE'):
        set_env_var(constants.sde_env_var_name, sde_home_absolute)
        set_env_var(constants.sde_install_env_var_name,
                    get_env_var(constants.sde_env_var_name) + '/install/')
        os.environ[constants.p4_prog_env_var_name] = get_p4_prog_name()
        append_to_env_var(constants.path_env_var_name, get_env_var(
            constants.sde_install_env_var_name) + '/bin/')
        print(
            'Environment variables set: \n SDE: {0} \n SDE_INSTALL: {1} \n PATH: {2} \n P4_PROG: {3}'.format(
                get_env_var(constants.sde_env_var_name),
                get_env_var(constants.sde_install_env_var_name),
                get_env_var(constants.path_env_var_name),
                get_env_var(constants.p4_prog_env_var_name)))
        return True
    else:
        print('ERROR: SDE directory couldnt be found, exiting .')
        exit(0)


def load_drivers():
    print('Loading kernel modules.')
    if not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        # exit(0)


def set_sde_env_n_load_drivers():
    set_sde_env()
    load_drivers()
    return True


def install_bsp_deps():
    os.system('sudo apt -y install libusb-1.0-0-dev libcurl4-openssl-dev')


def install_switch_bsp():
    set_sde_env()
    aps_bsp_installation_file = get_aps_bsp_pkg_abs_path()
    if (get_switch_model() == constants.bf6064x_t and (
            'BF2556' in aps_bsp_installation_file or 'bf2556' in aps_bsp_installation_file)) \
            or (get_switch_model() == constants.bf2556x_1t and (
            'BF6064' in aps_bsp_installation_file or 'bf6064' in aps_bsp_installation_file)):
        print("ERROR: Incompatible BSP provided in settings.yaml,"
              " Switch model is {model} but BSP is {bsp}".
              format(model=get_switch_model(),
                     bsp=aps_bsp_installation_file))
        exit(0)

    print("Installing {}".format(aps_bsp_installation_file))
    aps_zip = zipfile.ZipFile(aps_bsp_installation_file)
    aps_zip.extractall(Path(aps_bsp_installation_file).parent)
    aps_bsp_dir = aps_zip.namelist()[0] + '/apsn/'
    aps_bsp_dir_absolute = str(
        Path(aps_bsp_installation_file).parent) + '/' + aps_bsp_dir
    aps_zip.close()

    ref_bsp_tar = tarfile.open(get_ref_bsp_abs_path())
    ref_bsp_tar.extractall(Path(get_ref_bsp_abs_path()).parent)
    ref_bsp_dir = ref_bsp_tar.getnames()[0]
    os.chdir(str(
        Path(get_ref_bsp_abs_path()).parent) + '/' + ref_bsp_dir + '/packages')
    pltfm_tar_name = ''
    for f in os.listdir('./'):
        if f.endswith('.tgz'):
            pltfm_tar_name = f
    pltfm_tar = tarfile.open(pltfm_tar_name)
    pltfm_tar.extractall()
    bf_pltfm_dir = str(Path(
        get_ref_bsp_abs_path()).parent) + '/' + ref_bsp_dir + '/packages/' + \
        pltfm_tar.getnames()[0]

    aps_pltfm_dir = bf_pltfm_dir + '/platforms/apsn/'
    if os.path.exists(aps_pltfm_dir):
        shutil.rmtree(aps_pltfm_dir)

    shutil.copytree(aps_bsp_dir_absolute, aps_pltfm_dir)

    pltfm_tar.close()
    ref_bsp_tar.close()
    os.chdir(bf_pltfm_dir)
    os.system('patch -p1 < {0}/{1}'.format(str(
        Path(aps_bsp_installation_file).parent), get_diff_file_name()))
    # os.environ['BSP'] = os.getcwd()
    # print("BSP home directory set to {}".format(os.environ['BSP']))
    os.environ['BSP_INSTALL'] = get_env_var('SDE_INSTALL')
    print(
        "BSP_INSTALL directory set to {}".format(
            os.environ['BSP_INSTALL']))

    install_bsp_deps()
    os.system("autoreconf && autoconf")
    os.system("chmod +x ./autogen.sh")
    thrift_flag = ''
    if get_p4_studio_build_profile_name() != stratum_profile:
        thrift_flag = '--enable-thrift'
    if get_switch_model() == constants.bf2556x_1t:
        execute_cmd(
            "CFLAGS=-Wno-error ./configure --prefix={0} {1} "
            "--with-tof-brgup-plat".format(
                os.environ['BSP_INSTALL'], thrift_flag))
    else:
        execute_cmd(
            "CFLAGS=-Wno-error ./configure --prefix={0} {1}".format(
                os.environ['BSP_INSTALL'], thrift_flag))
    os.system("make")
    os.system("sudo make uninstall install")
    os.chdir(dname)
    return True


def just_load_sde():
    ask_user_for_building_sde()
    ask_user_for_building_bsp()
    prepare_sde_release()
    ask_user_for_starting_sde()


if __name__ == '__main__':
    do_basic_path_validation()
    just_load_sde()


def get_default_bsp_repo_path():
    if get_switch_model() == constants.bf2556x_1t:
        return get_abs_path(
            '/bsp/bf-reference-bsp-9.2.0-BF2556')
    elif get_switch_model() == constants.bf6064x_t:
        return get_abs_path(
            '/bsp/bf-reference-bsp-9.2.0-BF6064')
    else:
        print('Development BSp can\'t be retrieved for switch model'.
              format(get_switch_model()))
