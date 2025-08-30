pipeline {
    agent any
    environment {
        IMAGE_NAME = 'anas974/ml-retraining-app'  // Docker Hub repo name
        TAG = "${env.BUILD_NUMBER}"               // Build number for tagging
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
                    docker.build("${env.IMAGE_NAME}:${env.TAG}")
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
                    // Explicitly specifying Docker Hub registry URL to avoid URL errors
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-token') {
                        docker.image("${env.IMAGE_NAME}:${env.TAG}").push()
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
