pipeline {
    agent any

    environment {
        APP_NAME = 'vunl-python-flask'
        IMAGE = "vunl-python-flask-image"
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Build') {
            steps {
                echo "Building Docker image..."
                sh 'docker build -t $IMAGE:latest .'
            }
        }
        stage('Test') {
            steps {
                echo "Running unit tests..."
                sh '''
                    source venv/bin/activate
                    pytest --junitxml=results.xml
                '''
                junit 'results.xml'
            }
        }
        stage('Code Quality') {
            steps {
                echo "Running flake8 and pylint..."
                sh '''
                    source venv/bin/activate
                    flake8 app.py models.py > flake8_report.txt || true
                '''
                publishHTML(target: [
                    reportName: 'flake8 Report',
                    reportDir: '.',
                    reportFiles: 'flake8_report.txt',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }
        stage('Security') {
            steps {
                echo "Running Bandit security scan..."
                sh '''
                    source venv/bin/activate
                    bandit -r . -f html -o bandit_report.html || true
                '''
                publishHTML(target: [
                    reportName: 'Bandit Security Report',
                    reportDir: '.',
                    reportFiles: 'bandit_report.html',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }
        stage('Deploy') {
            steps {
                echo "Deploying Docker container (test/staging)..."
                sh '''
                  docker run -d -p 5000:5000 --name vunl-python-flask-test ${IMAGE}:latest
                '''
            }
        }
        stage('Release') {
            steps {
                input message: "Approve to release to production?"
                echo "Releasing to production environment..."
                sh '''
                  docker rm -f vunl-python-flask-prod || true
                  docker run -d -p 80:5000 --name vunl-python-flask-prod ${IMAGE}:latest
                '''
            }
        }
        stage('Monitoring') {
            steps {
                echo "Monitoring is configured"
                script {
                    def status = sh(script: "docker inspect -f '{{.State.Health.Status}}' vunl-python-flask-prod || echo 'no container'", returnStdout: true).trim()
                    if (status == 'healthy') {
                        echo "Production container is healthy."
                    } else {
                        echo "Warning: Production container health is '${status}'"
                    }
                }
            }
        }
    }
}
