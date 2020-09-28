pipeline {
    agent { label 'BF2556' }
    stages {
        stage('Clone AOT') {
            steps {
               git credentialsId: 'Jenkins_priv_ssh', url: 'https://github.com/stordis/APS-One-touch.git'
            }
        }
        stage('Clone SAL') {
            steps {
                dir('sal'){
                    git branch: 'SAL_Light', credentialsId: 'BF2556_ssh_key', url: "${sal_src}"
                }
            }
        }

        stage('Test AOT'){
            steps{
                sh 'PYTHONPATH=$PYTHONPATH:AOT python3 test/AOT_Test.py ~/jenkins_ci/settings.yaml'
            }
        }
    }
}
