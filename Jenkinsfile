pipeline {
    agent any
    
    environment {
        COMMIT_ID = "${GIT_COMMIT.take(5)}"
        BRANCH_NAME = "${GIT_BRANCH.split('/')[1]}" // Extracting the branch name from GIT_BRANCH variable
        BUILD_TAG = "${BRANCH_NAME}-${COMMIT_ID}" // Using the extracted branch name in the BUILD_TAG
        GIT_HELM_BRANCH = "ai-bot"
    }

    stages {
        stage('Logging into AWS ECR') {
            steps {
                script {
                    sh "aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 939638251740.dkr.ecr.ap-south-1.amazonaws.com/ai-bot-dev"
                }
            }
        }

        stage('Cloning Git') {
            steps {
                git branch: "${BRANCH_NAME}", changelog: false, credentialsId: 'gitNewstreettech', poll: false, url: 'https://github.com/NewStreetTechnologies/MiFiX_AI_Bot.git'
            }
        }

        stage('Building image') {
            steps {
                script {
                    sh "docker build -t 939638251740.dkr.ecr.ap-south-1.amazonaws.com/ai-bot-dev:${BUILD_TAG} ."
                }
            }
        }

        stage('Pushing to ECR') {
            steps {
                script {
                     sh "docker push 939638251740.dkr.ecr.ap-south-1.amazonaws.com/ai-bot-dev:${BUILD_TAG}"
                }
            }
        }

        stage("Remove image from Jenkins server") {  
            steps {
                sh "docker rmi 939638251740.dkr.ecr.ap-south-1.amazonaws.com/ai-bot-dev:${BUILD_TAG}"
            }
        }

        stage('Deployment on EKS') {
            steps { 
                script {
                    sh "ls"
                    sh 'git config --global credential.helper cache'
                    git branch: "${GIT_HELM_BRANCH}", credentialsId: 'gitNewstreettech', poll: false, url: 'https://github.com/NewStreetTechnologies/mifix-infra.git'
                    sh "git pull origin ${GIT_HELM_BRANCH}" 
                    sh "ls"
                    sh 'sed -i "s/tag: .*/tag: $BUILD_TAG/" ./ai-service/values.yaml'
                    sh "git add ./ai-service/values.yaml"
                    sh "git status"
                    sh 'git commit -m "CI/CD pipeline updated $BUILD_TAG image to new image tag"'
                    sh 'git config --global credential.helper cache'
                    sh "git push origin ${GIT_HELM_BRANCH}" 
                }
            }
        }
    }
}
