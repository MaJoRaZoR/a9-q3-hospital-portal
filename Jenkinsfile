pipeline {
  agent any
  options { disableConcurrentBuilds(); timestamps() }
  triggers { githubPush(); pollSCM('* * * * *') }
  parameters {
    booleanParam(name: 'FAULTY_RELEASE', defaultValue: false, description: 'Lab defect: reject kube-probe health requests')
  }
  environment {
    PATH = "C:/Users/viddu/AppData/Local/Programs/DockerDesktop/resources/bin;${env.PATH}"
    DOCKER_HOST = 'npipe:////./pipe/dockerDesktopLinuxEngine'
    APP = 'hospital'
    REPLICAS = '3'
    NODEPORT = '30083'
    PYTHONUTF8 = '1'
    DOCKER_CONFIG = "${WORKSPACE}/.docker-auth"
  }
  stages {
    stage('Clone Code') {
      steps { git branch: 'main', url: 'https://github.com/MaJoRaZoR/a9-q3-hospital-portal.git' }
    }
    stage('Build Docker Image') {
      steps {
        script {
          def sha = bat(script: '@git rev-parse --short=12 HEAD', returnStdout: true).trim()
          env.IMAGE = "majorazor/${env.APP}:${env.BUILD_NUMBER}-${sha}"
          env.BUILD_FILE = params.FAULTY_RELEASE ? 'Dockerfile.faulty' : 'Dockerfile'
        }
        bat 'docker build -f %BUILD_FILE% --build-arg RELEASE=%IMAGE% -t %IMAGE% .'
      }
    }
    stage('Test Application') { steps { bat 'python test.py' } }
    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
          bat '@python login.py'
          bat 'docker push %IMAGE%'
        }
      }
    }
    stage('Deploy Health Check and Automatic Rollback') {
      steps {
        withCredentials([file(credentialsId: 'kuberconfig', variable: 'KUBECONFIG')]) {
          bat 'python deploy.py'
        }
      }
    }
  }
  post {
    always {
      bat(returnStatus: true, script: '@docker logout')
      archiveArtifacts artifacts: 'rendered.yaml', allowEmptyArchive: true
    }
  }
}
