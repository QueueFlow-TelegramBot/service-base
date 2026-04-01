def dockerImage

pipeline {
    agent any

    environment {
        WS = env.JOB_NAME.split('-')[0..-2].join('-')
        ENV = env.JOB_NAME.split('-').last()
        IMAGE_NAME = "${DOCKERHUB_USERNAME}/${WS}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                githubNotify
                    context: 'Docker Build',
                    status: 'PENDING',
                    description: "Building Docker image for ${WS} in ${ENV}"

                script {
                    dockerImage = docker.build("${IMAGE_NAME}:${env.BUILD_ID}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                githubNotify
                    context: 'Docker Push',
                    status: 'PENDING',
                    description: "Pushing Docker image for ${WS} in ${ENV}"

                script {
                    echo "Docker Image Tag: ${IMAGE_NAME}:${env.BUILD_ID}"

                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub') {
                        dockerImage.push("${env.BUILD_NUMBER}")
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                githubNotify
                    context: 'Kubernetes Deploy',
                    status: 'PENDING',
                    description: "Deploying ${WS} to ${ENV} environment"

                script {
                    sh """
                    kubectl set image deployment/${WS}-${ENV} *=${IMAGE_NAME}:${env.BUILD_ID} --namespace=default
                    """
                }
            }
        }
    }

    post {
        always {
            emailext body: "Project: ${WS}\nBuild: ${env.BUILD_NUMBER}\nResult: ${currentBuild.currentResult}",
                     subject: "Deployment Notification: ${WS} - Build #${env.BUILD_NUMBER}",
                     to: ${MAIL_TO}
        }

        success {
            githubNotify context: 'Pipeline', status: 'SUCCESS', description: "Deployment successful for ${WS} in ${ENV}"
        }

        failure {
            githubNotify context: 'Pipeline', status: 'FAILURE', description: "Deployment failed for ${WS} in ${ENV}"
        }
    }
}