import os
import platform
import sys
import tarfile
import zipfile
from pathlib import Path
import subprocess
import yaml

import constants
from constants import sal_hw_profile_name, sal_sim_profile_name, \
    sde_hw_profile_name, sde_sim_profile_name, stratum_hw_profile_name, \
    stratum_sim_profile_name, BSP_node, aps_bsp_pkg_node, ref_bsp_node
import shutil

abspath = os.path.abspath(__file__)
# Absolute directory name containing this file
dname = os.path.dirname(abspath)


def read_settings():
    settings_file = None
    try:
        # Custom path for settings file can be given as CLI arg.
        settings_file = sys.argv[1]
    except IndexError:
        # If no settings file provided as CLI arg default one from the
        # project path will be picked.
        settings_file = "{}/settings.yaml".format(dname)

    if settings_file is None:
        print('Invalid settings file for AOT {}'.format(settings_file))
        exit(0)
    else:
        print('Reading settings from file {}'.format(settings_file))
        with open(settings_file, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                print("Error occurred while reading settings file {}".format(settings_file))
                exit(0)


settings_dict = read_settings()


def read_advance_settings():
    """
    Settings used for development.
    """
    advance_settings_file = "{}/advance_settings.yaml".format(dname)

    if advance_settings_file is None:
        print('Invalid settings file for AOT {}'.format(advance_settings_file))
        exit(0)
    else:
        print('Reading settings from file {}'.format(advance_settings_file))
        with open(advance_settings_file, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                print("Error occurred while reading settings file {}".
                      format(advance_settings_file))
                exit(0)


advance_settings_dict = read_advance_settings()


def get_bsp_dev_abs_path():
    return get_path_relative_to_user_home(
        get_from_advance_setting_dict(constants.BSP_node,
                                      constants.bsp_dev_node_name))


def delete_files(file):
    try:
        shutil.rmtree(file)
    except FileNotFoundError:
        print('{} already deleted'.format(file))
    except PermissionError:
        i = input('Alert! deleting file {}, y/n ?'.format(file))
        if i == 'y':
            os.system('sudo rm -rf {}'.format(file))
    except NotADirectoryError:
        os.system('rm {}'.format(file))


release_dir = dname + '/release'
if not os.path.exists(release_dir):
    os.mkdir(release_dir)


def check_path(some_path, path_for):
    if not os.path.exists(some_path):
        print(
            "ERROR: Invalid {0} path {1}.".format(path_for,
                                                  some_path))
        exit(0)
    return True


def validate_path_existence(some_path, path_for):
    if ':' in some_path:
        # in case when it is system path variable or so.
        for pth in some_path.split(':'):
            return check_path(pth, path_for)
    else:
        return check_path(some_path, path_for)


def get_kernel_major_version():
    rel = platform.release()
    rel_list = rel.split(".")
    return rel_list.pop(0) + "." + rel_list.pop(0)


def is_onl():
    if 'OpenNetworkLinux' in platform.release():
        print('Platform info {}'.format(
            platform.version()))
        return True
    return False


def is_ubuntu():
    if 'Ubuntu' in platform.version():
        print('Platform info {}'.format(
            platform.version()))
        return True
    return False


def get_path_prefix():
    p = get_from_setting_dict(constants.path_prefix_node)
    if not p:
        return str(Path.home())
    return p


def get_path_relative_to_user_home(pth):
    return get_path_prefix() + '/' + pth


def get_env_var(var_name):
    try:
        return os.environ[var_name]
    except KeyError as e:
        print('INFO: {} is not set.'.format(var_name))
        print(e)


def append_to_env_var(src_env_var_name, new_val_to_append):
    if get_env_var(src_env_var_name) is None:
        os.environ[src_env_var_name] = new_val_to_append
    else:
        os.environ[src_env_var_name] += os.pathsep + new_val_to_append


def set_env_var(var_name, var_val):
    """
    Sets env_var to var_val.
    """
    if validate_path_existence(var_val, var_name):
        os.environ[var_name] = var_val
        return True
    return False


def execute_cmd_n_get_output(cmd):
    """
    Returns console output of the command
    """
    print('Executing sys cmd : {}'.format(cmd))

    cmd_output = subprocess.run(cmd.split(' '), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    return cmd_output.stdout.decode('UTF-8')


def execute_cmd_n_get_output_2(cmd):
    return subprocess.check_output(cmd, shell=True).decode('UTF-8').strip()


def execute_cmd(cmd):
    print('Executing cmd : {}'.format(cmd))
    os.system(cmd)


def create_symlinks():
    # #currently following symlinks are necessary only in case of ONL.
    if is_onl():
        src = '/usr/share/onl/packages/amd64/onl-kernel-{}-lts-x86-64-all/mbuilds/'.format(
            get_kernel_major_version())
        # Needed to build sde.
        sde_symlink = '/lib/modules/{}/build'.format(platform.release())
        # needed to build irq.
        irq_symlink = '/usr/src/linux-headers-{}'.format(platform.release())
        if os.path.islink(sde_symlink):
            print('Removing symlink {}'.format(sde_symlink))
            os.unlink(sde_symlink)
        print('Creating symlink {}'.format(sde_symlink))
        os.symlink(src, sde_symlink)

        if os.path.islink(irq_symlink):
            print(print('Removing symlink {}'.format(irq_symlink)))
            os.unlink(irq_symlink)
        print('Creating symlink {}'.format(irq_symlink))
        os.symlink(src, irq_symlink)
    return True


def get_from_setting_dict(*keys):
    # keys to be in lexographic order
    val = settings_dict.copy()
    for key in keys:
        val = val.get(key)
    return val


def get_from_advance_setting_dict(*keys):
    # keys to be in lexographic order
    val = advance_settings_dict.copy()
    for key in keys:
        val = val.get(key)
    return val


def get_sde_pkg_abs_path():
    sde_pkg = get_path_relative_to_user_home(
        get_from_setting_dict('BF SDE', 'sde_pkg'))
    if not tarfile.is_tarfile(sde_pkg):
        print("Invalid tofino SDE tar file {} can not build.".format(sde_pkg))
        exit(0)
    return sde_pkg


def get_aps_bsp_pkg_abs_path():
    bsp_pkg = get_path_relative_to_user_home(
        get_from_setting_dict(BSP_node, aps_bsp_pkg_node))
    if not zipfile.is_zipfile(bsp_pkg):
        print("Invalid APS BSP zip file {} can not build.".format(bsp_pkg))
        exit(0)
    return bsp_pkg


def get_ref_bsp_abs_path():
    bsp_pkg = get_path_relative_to_user_home(
        get_from_setting_dict(BSP_node, ref_bsp_node))
    if not tarfile.is_tarfile(bsp_pkg):
        print("Invalid Reference BSP tar file {} can not build.".format(bsp_pkg))
        exit(0)
    return bsp_pkg


def get_sde_dir_name_in_tar():
    sde_tar = tarfile.open(get_sde_pkg_abs_path())
    sde_dir_name = sde_tar.getnames()[0]
    sde_tar.close()
    return sde_dir_name


def get_sde_home_absolute():
    sde_home_in_config = get_from_setting_dict('BF SDE', 'sde_home')
    if sde_home_in_config:
        # return absolute path as configured in yaml
        return get_path_relative_to_user_home(sde_home_in_config)
    # If not given in yaml, return sde_home relative to APS one touch
    return dname + '/' + get_sde_dir_name_in_tar()


def get_sde_install_dir_absolute():
    return get_sde_home_absolute() + '/install'


def get_sde_profile_dict():
    """
    Method returns sde profile dictionary valid for selected profile.
    """
    if get_selected_profile_name() in [sal_hw_profile_name,
                                       stratum_hw_profile_name]:
        return settings_dict.get(constants.build_profiles_node).get(
            constants.sde_hw_profile_node)
    elif get_selected_profile_name() in [sal_sim_profile_name,
                                         stratum_sim_profile_name]:
        return settings_dict.get(constants.build_profiles_node).get(
            constants.sde_sim_profile_node)
    elif get_selected_profile_name() in [sde_hw_profile_name,
                                         sde_sim_profile_name]:
        return get_selected_profile_dict()
    else:
        print(
            "Selected profile is not or doesn't have associated SDE profile !")


def get_sde_profile_name():
    return get_sde_profile_dict().get(constants.name_node)


def get_sde_profile_details():
    return get_sde_profile_dict().get(constants.details_node)


def get_sde_version():
    return get_sde_profile_details().get(constants.sde_version_node)


def get_selected_profile_dict():
    return settings_dict.get(constants.build_profiles_node).get(
        constants.selected_node)


def get_selected_profile_name():
    return get_selected_profile_dict().get(constants.name_node)


def get_gb_src_home_from_config():
    return advance_settings_dict.get('GB').get('gb_src')


def get_gb_src_home_absolute():
    return get_path_relative_to_user_home(get_gb_src_home_from_config())


def get_gb_lib_home_from_config():
    return advance_settings_dict.get('GB').get('gb_lib')


def get_gb_lib_home_absolute():
    return get_path_relative_to_user_home(get_gb_lib_home_from_config())


def get_switch_model_from_settings():
    return get_from_setting_dict(constants.switch_model_node)


def is_sim_profile_selected():
    return 'sim' in get_selected_profile_name()
