import os
import platform
import tarfile
from pathlib import Path
import subprocess
import yaml

import constants
from constants import sal_hw_profile_name, sal_sim_profile_name, \
    sde_hw_profile_name, sde_sim_profile_name, stratum_hw_profile_name, \
    stratum_sim_profile_name
import shutil

abspath = os.path.abspath(__file__)
# Absolute directory name containing this file
dname = os.path.dirname(abspath)

settings_dict = {}

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

release_dir=dname+'/release'
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
    return get_path_prefix()+ '/' + pth


def get_env_var(var_name):
    try:
        return os.environ[var_name]
    except KeyError as e:
        print('INFO: {} is not set.'.format(var_name))
        print(e)


def append_to_env_var(src_env_var_name, new_val):
    if get_env_var(src_env_var_name) is None:
        os.environ[src_env_var_name] = new_val
    else:
        os.environ[src_env_var_name] = get_env_var(
            src_env_var_name) + ':' + new_val


def set_env_var(var_name, var_val):
    """
    Sets env_var to var_val.
    """
    if validate_path_existence(var_val, var_name):
        os.environ[var_name] = var_val
        return True
    return False


def get_cmd_output(cmd):
    loaded_modules = subprocess.run(cmd.split(' '), stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    return loaded_modules.stdout.decode('UTF-8')


def install_deps():
    print("Installing dependencies...")
    # os.system("sudo apt install python python3 patch")


def create_symlinks():
    ##currently following symlinks are necessary only in case of ONL.
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


def read_settings():
    global settings_dict
    with open("{}/settings.yaml".format(dname), 'r') as stream:
        try:
            settings_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def get_from_setting_dict(*keys):
    ## keys to be in lexographic order
    val = settings_dict.copy()
    for key in keys:
        val = val.get(key)
    return val


def get_sde_pkg_name():
    sde_pkg = get_path_relative_to_user_home(
        get_from_setting_dict('BF SDE', 'sde_pkg'))
    if not tarfile.is_tarfile(sde_pkg):
        print("Invalid tofino SDE tar file {} can not build.".format(sde_pkg))
        return 0
    return sde_pkg


def get_sde_dir_name_in_tar():
    sde_tar = tarfile.open(get_sde_pkg_name())
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


def get_selected_profile_dict():
    return settings_dict.get(constants.build_profiles_node).get(
        constants.selected_node)


def get_selected_profile_name():
    return get_selected_profile_dict().get(constants.name_node)


def get_gb_home_from_config():
    return settings_dict.get('GB').get('gb_home')


def get_gb_home_absolute():
    return get_path_relative_to_user_home(get_gb_home_from_config())
