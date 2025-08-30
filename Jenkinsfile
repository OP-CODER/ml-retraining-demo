pipeline {
    agent any
    environment {
        IMAGE_NAME = 'anas974/ml-retraining-app'  // Replace with your Docker Hub username and repo
        REGISTRY = ''  // Empty to use default Docker Hub registry
        TAG = "${env.BUILD_NUMBER}"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Set Docker Context') {
            steps {
                bat 'docker context use default'
            }
        }
        stage('Docker Info Debug') {
            steps {
                bat 'docker info'
                bat 'docker context ls'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${TAG}")
                }
            }
        }
        stage('Test') {
            steps {
                echo 'No automated tests currently configured'
            }
        }
        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry(REGISTRY, 'docker-hub-token') {
                        docker.image("${IMAGE_NAME}:${TAG}").push()
                    }
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                echo 'Add your deployment steps here'
            }
        }
    }
    post {
        failure {
            echo 'Build or deployment failed.'
        }
        success {
            echo "Build ${env.BUILD_NUMBER} completed successfully."
        }
    }
}
