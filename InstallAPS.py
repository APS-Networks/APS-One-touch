import getpass
import os
import platform
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

installation_files = {
    "bsp": "./BF2556X-1T_BSP_9.0.0-master.zip",
    "sde": "./bf-sde-9.1.0.tar",
    "irq_debug_tgz": "./irq_debug.tgz",
    "mv_pipe_config_zip": "./mv_pipe_config.zip",
    "stratum_repo": "https://github.com/stratum/stratum.git"
}

installation_dir = {
    "sde_home": "./bf-sde-9.1.0"
}

abspath = os.path.abspath(__file__)
# Absolute directory name containing this file
dname = os.path.dirname(abspath)

print(
    "All or subset of following packages can be installed. Default path for "
    "searching following installation files is {}, or give custom path during "
    "installation :".format(
        dname))
for key, val in installation_files.items():
    print("{}{}{}".format(key, " -> ", val))


######################################################################
######################################################################

def install_deps():
    print("Installing dependencies...")
    # os.system("sudo apt install python python3 patch")


######################################################################
######################################################################
sde_folder_path = ""
sde = installation_files["sde"]

def build_sde(sde_path):
    print("Building SDE from {}.".format(sde_path))
    if not tarfile.is_tarfile(sde_path):
        print("Invalid tofino SDE tar file {} can not build.".format(sde_path))
        return 0

    sde_tar = tarfile.open(sde_path)
    sde_folder_name = sde_tar.getnames()[0]
    global sde_folder_path
    sde_folder_path = os.path.abspath(sde_folder_name)
    sde_tar.extractall()
    sde_tar.close()
    os.chdir(sde_folder_name)
    build_opt = "-up"
    default_profile = "p4_runtime_profile"
    profile_name = input(
        "Enter profile name to build SDE or i for interactive mode [{}]".format(
            default_profile))
    if not profile_name:
        profile_name = default_profile

    if profile_name == "i":
        build_opt = ""
        profile_name = ""

    sde_install_cmd = "./p4studio_build/p4studio_build.py {} {}".format(
        build_opt,
        profile_name)
    print(sde_install_cmd)
    os.system(sde_install_cmd)


def install_bf_sde():
    install_sde = input("Do you want to build SDE y/[n]?")
    if not install_sde:
        install_sde = "n"
    if install_sde == "y":
        sde_path = input("Enter the full path of sde tar [{}]?".format(sde))
        if not sde_path:
            sde_path = sde
        create_symlinks()
        build_sde(sde_path)
    else:
        print("You selected not to build SDE.")


######################################################################
######################################################################
def checkBF_SDE_Installation():
    global sde_folder_path
    if not os.path.exists(sde_folder_path):
        sde_folder_path = input(
            "Enter full path of Barefoot SDE installation directory[{0}]:".format(
                installation_dir["sde_home"]))
        if not sde_folder_path:
            sde_folder_path = dname + "/" + installation_dir["sde_home"]
            print("Using SDE {}".format(sde_folder_path))
            os.environ['SDE'] = sde_folder_path
            os.environ['SDE_INSTALL'] = os.environ['SDE'] + "/install"
        if not os.path.exists(sde_folder_path):
            print(
                "Invalid Barefoot SDE installation directory {}, Exiting "
                "installer.".format(
                    sde_folder_path))
            return False
    else:
        print(
            "Found BF SDE installation at {}.".format(
                sde_folder_path))
        return True


def install_switch_bsp():
    install_bsp = input("Do you want to build BSP y/[n]?")
    if not install_bsp:
        install_bsp = "n"
    if install_bsp == "y":
        checkBF_SDE_Installation()
        os.chdir(dname)
        bsp_installation_file = input(
            "Enter full path of BSP installation package [{}]".format(
                installation_files["bsp"]))
        if not bsp_installation_file:
            bsp_installation_file = installation_files["bsp"]
        if zipfile.is_zipfile(bsp_installation_file):
            print("Installing {}".format(bsp_installation_file))
            zip_ref = zipfile.ZipFile(bsp_installation_file)
            zip_ref.extractall()
            extracted_dir_name = zip_ref.namelist()[0]
            zip_ref.close()
            os.chdir(extracted_dir_name)
            os.environ['BSP'] = os.getcwd()
            print("BSP home directory set to {}".format(os.environ['BSP']))
            os.environ['BSP_INSTALL'] = "{}/install".format(sde_folder_path)
            print(
                "BSP_INSTALL directory set to {}".format(
                    os.environ['BSP_INSTALL']))
            os.chdir("bf-platforms-9.0.0")
            os.system("autoreconf && autoconf")
            os.system("chmod +x ./autogen.sh")
            os.system("chmod +x ./configure")
            os.system(
                "./configure --prefix={} --enable-thrift --with-tof-brgup-plat".format(
                    os.environ['BSP_INSTALL']))
            os.system("make")
            os.system("sudo make install")
    else:
        print("You choose not to install BSP.")


######################################################################
######################################################################

def get_cmd_output(cmd):
    loaded_modules = subprocess.run(cmd.split(' '), stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    return loaded_modules.stdout.decode('UTF-8')


def load_and_verify_kernel_modules():
    output = get_cmd_output('lsmod')
    irq_debug = True
    bf_kdrv = True
    mv_pipe = True

    os.system("sudo modprobe -q i2c-i801")
    os.system("sudo modprobe -q i2c-dev")

    if 'irq_debug' not in output:
        install_irq_debug()

    if 'bf_kdrv' not in output:
        load_bf_kdrv()

    if not os.path.exists("/delta/mv_pipe_config"):
        install_mv_pipe()

    loaded_modules = subprocess.run(['lsmod'], stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    output = loaded_modules.stdout.decode('UTF-8')

    if 'irq_debug' not in output:
        irq_debug = False
        print("ERROR:irq_debug is not loaded.")

    if 'bf_kdrv' not in output:
        irq_debug = False
        print("ERROR:bf_kdrv is not loaded.")

    if not os.path.exists("/delta/mv_pipe_config"):
        mv_pipe = False
        print("ERROR:mv_pipe_config not installed.")

    # TODO Check for i2c modules to be loaded as well.

    return irq_debug and bf_kdrv and mv_pipe


def alloc_dma():
    output=get_cmd_output('cat /etc/sysctl.conf')
    if 'vm.nr_hugepages = 128' not in output:
        print('Setting up huge pages...')
        dma_alloc_cmd = 'sudo /{}/pkgsrc/ptf-modules/ptf-utils/dma_setup.sh'.format(
                sde_folder_path)
        os.system(dma_alloc_cmd)


def start_bf_switchd():
    os.chdir(dname)
    checkBF_SDE_Installation()
    if not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)
    p4_prog_name = input(
        "Enter P4 program name to start switchd with or leave blank:")

    # LD_LIBRARY_PATH is set for ONLPv2 case, libs in install/lib folder are
    # not found there but this does not cause any harm for Ubuntu case either.
    os.environ['LD_LIBRARY_PATH'] = "/{0}/install/lib".format(
        sde_folder_path)
    os.system("echo $LD_LIBRARY_PATH")

    if not p4_prog_name:
        print("Starting switchd without p4 program")
        start_switchd_cmd = "sudo {0}/install/bin/bf_switchd --install-dir {" \
                            "0}/install --conf-file {" \
                            "0}/pkgsrc/p4-examples/tofino/tofino_skip_p4.conf" \
                            ".in --skip-p4".format(sde_folder_path)
    else:
        print("Starting switchd with P4 prog:{}".format(p4_prog_name))
        start_switchd_cmd = sde_folder_path + "/run_switchd.sh -p {}".format(
            p4_prog_name.replace(".p4", ""))
    username = getpass.getuser()

    if username == "root":
        start_switchd_cmd = start_switchd_cmd.replace("sudo", "")
    alloc_dma()
    print("Starting switchd with command : {}".format(start_switchd_cmd))
    os.system(start_switchd_cmd)


######################################################################
######################################################################

def install_irq_debug():
    print("Installing irq_debug...")
    os.chdir(dname)
    print("Working dir :{}".format(dname))
    irq = installation_files["irq_debug_tgz"]
    irq_file_path = input(
        "Enter path for irq_debug_driver [{}]".format(irq))
    if irq_file_path:
        irq = irq_file_path
    print("Installing irq debug drivers.")
    create_symlinks()
    tar = tarfile.open(irq)
    irq_folder_name = tar.getnames()[0]
    tar.extractall()
    tar.close()
    print(irq_folder_name)
    os.chdir(irq_folder_name)
    os.system("make")

    print("Installing module irq_debug.")
    os.system("sudo insmod ./irq_debug.ko")


######################################################################
######################################################################


def install_mv_pipe():
    print("Building mv_pipe_config...")
    os.chdir(dname)
    mv_pipe = installation_files["mv_pipe_config_zip"]
    mv_pipe_path = input(
        "Enter path for mv_pipe package [{}]".format(mv_pipe))
    if mv_pipe_path:
        mv_pipe = mv_pipe_path
    zip_ref = zipfile.ZipFile(mv_pipe)
    zip_ref.extractall()
    extracted_dir_name = zip_ref.namelist()[0]
    zip_ref.close()
    os.chdir(extracted_dir_name)
    os.system("gcc mv_pipe_config.c -o mv_pipe_config")
    os.system("sudo mkdir /delta")
    os.system("sudo cp ./mv_pipe_config /delta/")


######################################################################
######################################################################

def load_bf_kdrv():
    print("Loading bf_kdrv....")
    checkBF_SDE_Installation()
    print("Using SDE {} for loading bf_kdrv.".format(sde_folder_path))
    os.system(
        "sudo {}/install/bin/bf_kdrv_mod_load {}/install/".format(
            sde_folder_path, sde_folder_path))


######################################################################
######################################################################
def set_stratum_env():
    checkBF_SDE_Installation()
    os.environ['BF_SDE_INSTALL'] = "/{0}/install/".format(sde_folder_path)
    os.environ['LD_LIBRARY_PATH'] = "/{0}/lib:/lib/x86_64-linux-gnu".format(
        os.environ['BF_SDE_INSTALL'])
    os.environ['PI_INSTALL'] = os.environ['BF_SDE_INSTALL']
    os.environ['CONFIG_DIR'] = str(Path.home()) + "/config"
    os.environ['STRATUM_HOME'] = str(Path.home()) + "/stratum"

    print('Env for starting Stratum :\n{0}\n{1}\n{2}\n{3}\n{4}'.format(
        'BF_SDE_INSTALL {}'.format(os.environ['BF_SDE_INSTALL']),
        'LD_LIBRARY_PATH {}'.format(os.environ['LD_LIBRARY_PATH']),
        'PI_INSTALL {}'.format(os.environ['PI_INSTALL']),
        'CONFIG_DIR {}'.format(os.environ['CONFIG_DIR']),
        'STRATUM_HOME {}'.format(os.environ['STRATUM_HOME'])))


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


def get_kernel_major_version():
    rel = platform.release()
    rel_list = rel.split(".")
    return rel_list.pop(0) + "." + rel_list.pop(0)


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


def start_stratum():
    if not is_onl():
        print('ERROR: Stratum is not supported on this platform {}'.format(
            platform.version()))
        exit(0)
    print("Starting Stratum....")
    set_stratum_env()
    stratum_start_cmd_bsp_less = '{0}/bazel-bin/stratum/hal/bin/barefoot/stratum_bf \
    --external_stratum_urls=0.0.0.0:28000 \
    --grpc_max_recv_msg_size=256 \
    --bf_sde_install={1} \
    --persistent_config_dir={2} \
    --forwarding_pipeline_configs_file={2}/p4_pipeline.pb.txt \
    --chassis_config_file={2}/chassis_config.pb.txt \
    --write_req_log_file={2}/p4_writes.pb.txt \
    --bf_switchd_cfg={0}/stratum/hal/bin/barefoot/tofino_skip_p4_no_bsp.conf'.format(
        os.environ['STRATUM_HOME'],
        os.environ['BF_SDE_INSTALL'],
        os.environ['CONFIG_DIR']
    )

    stratum_start_cmd_bsp = '{0}/bazel-bin/stratum/hal/bin/barefoot/stratum_bf \
        --external_stratum_urls=0.0.0.0:28000 \
        --grpc_max_recv_msg_size=256 \
        --bf_sde_install={1} \
        --persistent_config_dir={2} \
        --forwarding_pipeline_configs_file={2}/p4_pipeline.pb.txt \
        --chassis_config_file={2}/chassis_config.pb.txt \
        --write_req_log_file={2}/p4_writes.pb.txt \
        --bf_sim'.format(
        os.environ['STRATUM_HOME'],
        os.environ['BF_SDE_INSTALL'],
        os.environ['CONFIG_DIR']
    )

    print("Using SDE {} for loading bf_kdrv.".format(sde_folder_path))
    os.system(
        "sudo {}/install/bin/bf_kdrv_mod_unload {}/install/".format(
            sde_folder_path, sde_folder_path))
    os.system(
        "sudo {}/install/bin/bf_kdrv_mod_load {}/install/".format(
            sde_folder_path, sde_folder_path))

    stratum_start_mode = input("Select start mode of stratum [bsp-less]/bsp?")
    if not stratum_start_mode:
        stratum_start_mode = 'bsp-less'

    shutil.copyfile(os.environ['STRATUM_HOME']+'/stratum/hal/bin/barefoot/platforms/x86-64-stordis-bf2556x-1t-r0.json',
                    os.environ['BF_SDE_INSTALL']+'/share/port_map.json')

    if stratum_start_mode == 'bsp-less':
        print("Starting Stratum in bsp-less mode...")
        print(stratum_start_cmd_bsp_less)
        os.system(stratum_start_cmd_bsp_less)
    else:
        print("Starting Stratum in bsp-less mode...")
        print(stratum_start_cmd_bsp_less)
        os.system(stratum_start_cmd_bsp_less)

def clone_stratum():
    os.system('git clone https://github.com/stratum/stratum.git')

def compile_stratum():
    print('Buidlding stratum...')
    set_stratum_env()
    stratum_build_command = 'bazel build //stratum/hal/bin/barefoot:stratum_bf'
    os.chdir(os.environ['STRATUM_HOME'])
    print('Executing : {}'.format(stratum_build_command))
    os.system(stratum_build_command)

    ######################################################################
    ######################################################################


if __name__ == '__main__':
    install_deps()
    install_bf_sde()
    install_switch_bsp()
    start_switchd = input("Do you want to start [switchd]/stratum?")
    if not start_switchd:
        start_switchd = "switchd"
    if start_switchd == "switchd":
        start_bf_switchd()
    else:
        build_stratum = input("Do you want to build stratum y/[n]?")
        if not build_stratum:
            build_stratum = "n"
        if build_stratum == "y":
            stratum_clone = input("Do you want to clone stratum or provide code location y/[./stratum]?")
            if not stratum_clone:
                build_stratum = "n"
            if stratum_clone == 'y':
                clone_stratum()
            compile_stratum()
        run_stratum = input("Do you want to start stratum y/[n]?")
        if not run_stratum:
            run_stratum = "n"
        if run_stratum == "y":
            start_stratum()
