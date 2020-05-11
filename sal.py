import os
import shutil

import common
from bf_sde import checkBF_SDE_Installation
from common import set_env_relative_to_user_home, get_from_setting_dict


def set_sal_env():
    if not checkBF_SDE_Installation():
        exit()
    os.environ['TCMALLOC_LARGE_ALLOC_REPORT_THRESHOLD'] = '64077925800531312640'
    set_env_relative_to_user_home('SAL_HOME',common.settings_dict.get('SAL').get('sal_home'))
    set_env_relative_to_user_home('PYTHONPATH',common.settings_dict.get('SAL').get('sal_home'))
    set_env_relative_to_user_home('BF_HOME',
                                  common.get('BF SDE').get('sde_home'))
    set_env_relative_to_user_home('BF_INSTALL',common.settings_dict.get('BF SDE').get('sde_home')+'/install')
    set_env_relative_to_user_home('BF_INCLUDE',
                                  common.settings_dict.get('BF SDE').
                                  get('sde_home')+'/install/include')
    set_env_relative_to_user_home('GB_HOME',
                                  common.settings_dict.get('GB').
                                  get('gb_home'))
        
    print('SAL_HOME: {0} \
    \n PYTHONPATH: {1} \
    \n BF_HOME: {2} \
    \n BF_INSTALL: {3} \
    \n BF_INCLUDE: {4} \
    \n GB_HOME: {5}'.format(
    os.environ['SAL_HOME'],
    os.environ['PYTHONPATH'],
    os.environ['BF_HOME'],
    os.environ['BF_INSTALL'],
    os.environ['BF_INCLUDE'],
    os.environ['GB_HOME']))
    return True
    
def build_sal():
    print('Building SAL...')
    set_sal_env()
    #os.chdir(os.environ['SAL_HOME'])
    os.system('cmake {}'.format(os.environ['SAL_HOME']))
    os.system('make -C {}'.format(os.environ['SAL_HOME']))
    
def clean_sal():
    print('Cleaning SAL...')
    set_sal_env()
    build_dir=os.environ['SAL_HOME']+'/build'
    log_dir=os.environ['SAL_HOME']+'/logs/'
    print('Cleaning build...')
    os.system('make -C {} clean'.format(os.environ['SAL_HOME']))
    print('Deleting {}'.format(build_dir))
    shutil.rmtree(build_dir, ignore_errors=True)
    print('Deleting {}'.format(log_dir))
    shutil.rmtree(log_dir,ignore_errors=True)

def run_sal():
    print('Starting SAL reference application...')
    set_sal_env()
    sal_executable=os.environ['SAL_HOME']+'/build/salRefApp'
    os.system('sudo -E {}'.format(sal_executable))

def test_sal():
    print("To be integrated")

def load_sal_profile():
    load_
    sal_input = input("Do you want to [build],clean,run,test sal?")
    if sal_input== 'clean':
        clean_sal()
    elif sal_input=='run':
        run_sal()
    elif sal_input=='test':
        test_sal()
    else:
        build_sal()
