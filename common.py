import os
import platform
import sys
import tarfile
import zipfile
from pathlib import Path
import subprocess
import yaml

import constants
from constants import BSP_node, aps_bsp_pkg_node, ref_bsp_node, \
    switch_model_env_var_name, bf2556x_1t, bf6064x_t, p4_prog_node_name
import shutil

abspath = os.path.abspath(__file__)
# Absolute directory name containing this file
dname = os.path.dirname(abspath)


def read_settings():
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
    try:
        # Custom path for settings file can be given as CLI arg.
        advance_settings_file = sys.argv[2]
    except IndexError:
        # If no settings file provided as CLI arg default one from the
        # project path will be picked.
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


aot_release_dir = dname + '/release'
if not os.path.exists(aot_release_dir):
    os.mkdir(aot_release_dir)


def get_latest_git_tag(local_git_repo):
    return execute_cmd_n_get_output_2(
        'git --git-dir {0}/.git describe --abbrev=0 --tags'.
        format(local_git_repo)).strip()


def get_git_tag_hash(local_git_repo, git_tag):
    return execute_cmd_n_get_output_2(
        'git --git-dir {0}/.git rev-list -n 1 {1}'.
        format(local_git_repo, git_tag))


def get_latest_git_hash(local_git_repo):
    return execute_cmd_n_get_output_2(
        'git --git-dir {0}/.git rev-parse HEAD'.
        format(local_git_repo))


def get_2nd_latest_git_tag(local_git_repo):
    # If only one tag exists then second last release tag refers to previous
    # commit hash to latest release tag.
    return execute_cmd_n_get_output_2(
        'git --git-dir {0}/.git describe --abbrev=0 --tags `git --git-dir {0}/.git rev-list --tags --skip=1 '
        '--max-count=1` --always'.
        format(local_git_repo)).strip()


def create_nested_dir(destination_location, dir_path):
    """
    Creates nested path given in @dir_path string inside @destination_location,
    the outermost directory is ignored and that can be copied by calling function when
    all parent directory structure is present.
    Args:
        destination_location:
        dir_path:
    Returns:
    """
    nested_path_list = dir_path.split('/')
    # clear up empty strings in the path
    nested_path_list = list(filter(None, nested_path_list))
    # Slice the last dir
    nested_path_list = nested_path_list[:-1]
    for d in nested_path_list:
        destination_location += '/' + d + '/'
        if not os.path.exists(destination_location):
            os.mkdir(destination_location)


def create_release(local_git_repo, files_to_release):
    """

    Args:
        local_git_repo: Absolute path to local git repository
        files_to_release: File paths relative to local_git_repo to be part of release.
    Returns:

    """
    rel_tag_latest = get_latest_git_tag(local_git_repo)
    release_tag_2ndlast = get_2nd_latest_git_tag(local_git_repo)
    hash_rel_tag_latest = get_git_tag_hash(local_git_repo, rel_tag_latest)
    hash_latest = get_latest_git_hash(local_git_repo)

    if hash_latest == hash_rel_tag_latest:
        print('Preparing main release {}'.format(rel_tag_latest))
        print('Preparing release notes since release tag {}'.format(
            release_tag_2ndlast))
        start_hash_for_rn = release_tag_2ndlast
        end_hash_for_rn = rel_tag_latest
        arch_name = aot_release_dir + '/{0}_{1}'. \
            format(os.path.basename(local_git_repo), rel_tag_latest)
    else:
        print('Preparing development release.')
        start_hash_for_rn = rel_tag_latest
        end_hash_for_rn = hash_latest
        suffix = execute_cmd_n_get_output_2(
            'git --git-dir {0}/.git describe --tags'.
            format(local_git_repo)).strip()
        arch_name = aot_release_dir + '/{0}_{1}'. \
            format(os.path.basename(local_git_repo), suffix)

    try:
        os.mkdir(arch_name)
        print('Release directory {} created.'.format(arch_name))
    except FileExistsError:
        print('Release directory {} already exists, recreated.'.format(
            arch_name))
        delete_files(arch_name)
        os.mkdir(arch_name)

    rel_notes_file = 'RelNotes_{}.txt'.format(os.path.basename(os.path.normpath(arch_name)))
    make_rel_notes(local_git_repo, rel_notes_file, start_hash_for_rn, end_hash_for_rn)
    for arr in files_to_release:
        abs_file_path = arr[0] + '/' + arr[1]
        create_nested_dir(arch_name, arr[1])
        if os.path.isdir(abs_file_path):
            shutil.copytree(abs_file_path, arch_name + '/' + arr[1])
        else:
            shutil.copyfile(abs_file_path, arch_name + '/' + arr[1])
    shutil.copyfile(local_git_repo + '/' + rel_notes_file, arch_name + '/' + rel_notes_file)
    shutil.make_archive(arch_name, 'zip', arch_name)
    print('Release is available at {}'.format(aot_release_dir))


def make_rel_notes(local_git_repo, rel_notes_file, start_hash_for_rn, end_hash_for_rn):
    cmd = 'git --git-dir {0}/.git log --pretty=format:%s {2}..{3} > {0}/{1}'. \
        format(local_git_repo, rel_notes_file, start_hash_for_rn, end_hash_for_rn)

    print('Executing command : {}'.format(cmd))
    os.system(cmd)


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


def get_abs_path(pth):
    return get_path_prefix() + '/' + pth


def get_env_var(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        print('INFO: env_var {} is not set.'.format(var_name))


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
    sde_pkg = get_abs_path(
        get_from_setting_dict('BF SDE', 'sde_pkg'))
    if not tarfile.is_tarfile(sde_pkg):
        print("Invalid tofino SDE tar file {} can not build.".format(sde_pkg))
        exit(0)
    return sde_pkg


def get_aps_bsp_pkg_abs_path():
    bsp_pkg = get_abs_path(
        get_from_setting_dict(BSP_node, aps_bsp_pkg_node))
    return bsp_pkg


def get_ref_bsp_abs_path():
    bsp_pkg = get_abs_path(
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
        return get_abs_path(sde_home_in_config)
    # If not given in yaml, return sde_home relative to APS one touch
    return dname + '/' + get_sde_dir_name_in_tar()


def get_sde_install_dir_absolute():
    return get_sde_home_absolute() + '/install'


def get_gb_src_home_from_config():
    return advance_settings_dict.get('GB').get('gb_src')


def get_gb_src_home_absolute():
    return get_abs_path(get_gb_src_home_from_config())


def get_gb_lib_home_from_config():
    return advance_settings_dict.get('GB').get('gb_lib')


def get_gb_lib_home_absolute():
    return get_abs_path(get_gb_lib_home_from_config())


def get_switch_model_from_env():
    model_name = get_env_var(switch_model_env_var_name)
    if model_name is None or model_name not in [bf2556x_1t, bf6064x_t]:
        print('Please set env_var SWITCH_MODEL with values either {0} or {1}, '
              'e.g.- export SWITCH_MODEL={0}'.
              format(bf2556x_1t, bf6064x_t))
        exit(0)
    return model_name


def get_switch_model():
    output = execute_cmd_n_get_output_2('sudo dmidecode -s system-product-name')
    if 'BF2556' in output:
        switch_model = bf2556x_1t
    elif 'BF6064' in output:
        switch_model = bf6064x_t
    else:
        print('Switch model couldn\'t be retrieved from System, Checking environment for {}'.
              format(switch_model_env_var_name))
        switch_model = get_switch_model_from_env()
    return switch_model


print("Switch model is", get_switch_model())


def get_p4_prog_name():
    p4_prog_name = get_from_setting_dict('BF SDE', p4_prog_node_name)
    if p4_prog_name is None:
        p4_prog_name = ''
    return p4_prog_name


def do_basic_path_validation():
    # Do basic path verification.
    validate_path_existence(get_sde_pkg_abs_path(), 'Barefoot SDE')
