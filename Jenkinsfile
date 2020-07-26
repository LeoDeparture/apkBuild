def build_env

// provides corresponding values of the environment
// need a girlfriend
if  (env.BRANCH_NAME == "develop") {
  build_env = 'dev'
} else if  (env.BRANCH_NAME =~ /^release\/.*/) {
   build_env = 'staging'
} else if  (env.BRANCH_NAME == "master") {
   build_env = 'release'
}

def isBuildPlanned(branch){
    return branch =~ "^master|^develop|^release/.*"
}

pipeline {
  agent { label 'apk-builder' }
  options {
    timestamps()
  }
  environment {
    CI = 'true'
  }
  stages {
    stage('Build-apk') {
      when {
        expression{ isBuildPlanned(env.BRANCH_NAME) }
      }
      steps {
        script {
          sh "/usr/local/bin/python3 /root/npmBuild.py ${build_env} ${env.BUILD_NUMBER} "
        }
      }
    }
  }
}