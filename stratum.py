import os
def start_stratum(stratum_mode):

    print("Starting Stratum....")
    set_stratum_env()
    stratum_start_cmd_bsp_less = 'sudo {0}/bazel-bin/stratum/hal/bin/barefoot/stratum_bf \
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

    stratum_start_cmd_bsp = 'sudo LD_LIBRARY_PATH=$BF_SDE_INSTALL/lib {0}/bazel-bin/stratum/hal/bin/barefoot/stratum_bf \
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
        os.environ['CONFIG_DIR'],
        os.environ['LD_LIBRARY_PATH']
    )

    if not load_and_verify_kernel_modules():
        print("ERROR:Some kernel modules are not loaded.")
        exit(0)

    shutil.copyfile(os.environ[
                        'STRATUM_HOME'] + '/stratum/hal/bin/barefoot/platforms/x86-64-stordis-bf2556x-1t-r0.json',
                    os.environ['BF_SDE_INSTALL'] + '/share/port_map.json')
    os.chdir(os.environ['STRATUM_HOME'])
    print('Current dir: {}'.format(os.getcwd()))
    if stratum_mode == 'bsp-less':
        print("Starting Stratum in bsp-less mode...")
        print("Executing command {}".format(stratum_start_cmd_bsp_less))
        os.system(stratum_start_cmd_bsp_less)
    else:
        print("Starting Stratum in bsp mode...")
        print("Executing command {}".format(stratum_start_cmd_bsp))
        os.system(stratum_start_cmd_bsp)


def clone_stratum():
    os.system('git clone {}'.format(settings_dict.get('STRATUM').get('stratum_repo')))

def set_stratum_env():
    checkBF_SDE_Installation()
    set_env_relative_to_user_home('BF_SDE_INSTALL', settings_dict.get('BF SDE').get('sde_home')+'/install')
    os.environ['LD_LIBRARY_PATH'] = "/{0}/lib:/lib/x86_64-linux-gnu".format(
        os.environ['BF_SDE_INSTALL'])
    os.environ['PI_INSTALL'] = os.environ['BF_SDE_INSTALL']
    
    set_env_relative_to_user_home('CONFIG_DIR', settings_dict.get('STRATUM').get('config'))
    set_env_relative_to_user_home('STRATUM_HOME', settings_dict.get('STRATUM').get('stratum_home'))
    set_env_relative_to_user_home('ONLP_INSTALL', "/onlp-dev_1.0.1_amd64" )
    set_env_relative_to_user_home('SAL_HOME', settings_dict.get('SAL').get('sal_home'))

    print('Env for starting Stratum :\n{0}\n{1}\n{2}\n{3}\n{4}\n{5}'.format(
        'BF_SDE_INSTALL {}'.format(os.environ['BF_SDE_INSTALL']),
        'LD_LIBRARY_PATH {}'.format(os.environ['LD_LIBRARY_PATH']),
        'PI_INSTALL {}'.format(os.environ['PI_INSTALL']),
        'CONFIG_DIR {}'.format(os.environ['CONFIG_DIR']),
        'STRATUM_HOME {}'.format(os.environ['STRATUM_HOME']),
        'SAL_HOME {}'.format(os.environ['SAL_HOME'])
    ))

def compile_stratum(stratum_mode):
    print('Building stratum...')
    print('Current working dir {}'.format(os.getcwd()))
    set_stratum_env()
    stratum_build_command = 'bazel build //stratum/hal/bin/barefoot:stratum_bf --define phal_with_gb=true'
    if stratum_mode == 'bsp':
        stratum_build_command = stratum_build_command + ' --define phal_with_onlp=false'
    stratum_clean_cmd = 'bazel clean'
    os.chdir(os.environ['STRATUM_HOME'])

    print('Executing : {}'.format(stratum_clean_cmd))
    os.system(stratum_clean_cmd)

    print('Executing : {}'.format(stratum_build_command))
    os.system(stratum_build_command)


def clean_stratum(stratum_mode):
    print('Cleaning stratum...')
    print('Current working dir {}'.format(os.getcwd()))
    set_stratum_env()
    stratum_clean_cmd = 'bezel clean'
    os.chdir(os.environ['STRATUM_HOME'])
    print('Executing : {}'.format(stratum_clean_cmd))
    os.system(stratum_clean_cmd)
    
def load_stratum_profile(profile_details):
    build_stratum = input("Do you want to build stratum y/[n]?")
    stratum_start_mode = profile_details.get('selected_mode')
         
    if not build_stratum:
        build_stratum = "n"
        
    if build_stratum == "y":
        stratum_dir = input(
            "Do you want to clone stratum or provide stratum_home \
             location y/[{}]?".format(profile_details.get('stratum_home')))
        if not stratum_dir:
            stratum_dir = profile_details.get('stratum_home')
        if stratum_dir == 'y':
            clone_stratum()
        compile_stratum(stratum_start_mode)
    run_stratum = input("Do you want to start stratum y/[n]?")
    if not run_stratum:
        run_stratum = "n"
    if run_stratum == "y":
        start_stratum(stratum_start_mode)