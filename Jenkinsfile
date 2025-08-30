pipeline {
    agent any
    environment {
        IMAGE_NAME = 'anas974/ml-retraining-app'  // Replace with your Docker Hub username and repo
        REGISTRY = 'registry.hub.docker.com'
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
                // Add your tests or linting commands here
                echo 'No automated tests currently configured'
            }
        }
        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", 'docker-hub-credentials') {  // Replace with your Jenkins Docker Hub credentials ID
                        docker.image("${IMAGE_NAME}:${TAG}").push()
                    }
                }
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                // Add your kubectl or helm deployment commands here
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
