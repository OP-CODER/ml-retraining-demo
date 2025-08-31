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
        AWS_ACCOUNT_ID = '108782070222'
        AWS_REGION = 'us-east-1'
        REPO_NAME = 'ml-retraining-demo'
        IMAGE_NAME = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"
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
                sh 'docker context use default'
            }
        }
        stage('Docker Info Debug') {
            steps {
                sh 'docker info'
                sh 'docker context ls'
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
        stage('Push to ECR') {
            steps {
                script {
                    withAWS(region: "${env.AWS_REGION}", credentials: 'aws-credentials-id') {
                         sh """
                           aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                           docker push ${IMAGE_NAME}:${TAG}
                          """
                    }
                }
            }
        }
        stage('Verify kubectl access') {
            steps {
                sh 'kubectl get nodes'
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    def serviceType = params.K8S_ENV == 'EKS' ? 'LoadBalancer' : 'NodePort'
                    def deploymentYaml = readFile('k8s/deployment.yml').replace('{{TAG}}', env.TAG)
                    def serviceYaml = readFile('k8s/service.yml').replace('{{SERVICE_TYPE}}', serviceType)
                    writeFile file: 'deployment-temp.yml', text: deploymentYaml
                    writeFile file: 'service-temp.yml', text: serviceYaml
                    sh 'kubectl apply -f deployment-temp.yml'
                    sh 'kubectl apply -f service-temp.yml'
                    sh 'kubectl rollout status deployment/ml-model-deployment'
                }
            }
        }
        stage('Publish Metrics') {
            steps {
                sh 'dir training\\metrics.json'  // Verify metric file exists
                archiveArtifacts artifacts: 'training/metrics.json', allowEmptyArchive: true
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
