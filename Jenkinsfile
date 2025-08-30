pipeline {
    agent any
    parameters {
        choice(
            name: 'K8S_ENV',
            choices: ['LOCAL', 'EKS'],
            description: 'Select Kubernetes environment to deploy to'
        )
    }
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
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-token') {
                        docker.image("${env.IMAGE_NAME}:${env.TAG}").push()
                    }
                }
            }
        }
        stage('Verify kubectl access') {
            steps {
                bat 'kubectl get nodes'
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    def serviceType = params.K8S_ENV == 'EKS' ? 'LoadBalancer' : 'NodePort'

                    // Read manifests with placeholders
                    def deploymentYaml = readFile('deployment.yml').replace('{{TAG}}', env.TAG)
                    def serviceYaml = readFile('service.yml').replace('{{SERVICE_TYPE}}', serviceType)

                    // Write replaced manifests to temp files
                    writeFile file: 'deployment-temp.yml', text: deploymentYaml
                    writeFile file: 'service-temp.yml', text: serviceYaml

                    // Apply manifests and monitor rollout
                    bat 'kubectl apply -f deployment-temp.yml'
                    bat 'kubectl apply -f service-temp.yml'
                    bat 'kubectl rollout status deployment/ml-model-deployment'
                }
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
