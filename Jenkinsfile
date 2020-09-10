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
                git credentialsId: 'Jenkins_priv_ssh', url: 'git@github.com:stordis/sal.git'
            }
        }
        
        stage('Build SAL') {
            steps {
                echo 'Building SAL.'
            }
        }
        
        stage('Test SAL') {
            steps {
                echo 'Testing SAL.'
            }
        }
        
    }
   
}
