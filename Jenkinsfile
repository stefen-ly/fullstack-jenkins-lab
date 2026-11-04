
pipeline {
    agent { label 'docker-ready' }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker compose up -d --no-build'
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    curl -fsS --retry 15 \
                    --retry-delay 2 \
                    --retry-connrefused \
                    http://127.0.0.1:8090/api/health
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline SUCCESS!'
        }

        failure {
            echo 'Pipeline FAILED!'
        }

        always {
            script {
                def status = currentBuild.currentResult

                // Email Notification
                try {
                    emailext(
                        to: 'vanlythouern51@gmail.com',
                        subject: "Jenkins ${status}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: """
Jenkins CI/CD Notification

Status: ${status}
Job: ${env.JOB_NAME}
Build: #${env.BUILD_NUMBER}
Build URL: ${env.BUILD_URL}
"""
                    )
                } catch (err) {
                    echo "Email notification failed: ${err.message}"
                }

                // Telegram Notification
                try {
                    withCredentials([
                        string(
                            credentialsId: 'telegram-bot-token',
                            variable: 'TELEGRAM_BOT_TOKEN'
                        ),
                        string(
                            credentialsId: 'telegram-chat-id',
                            variable: 'TELEGRAM_CHAT_ID'
                        )
                    ]) {
                        withEnv(["NOTIFY_STATUS=${status}"]) {
                            sh '''
                                set +x
                                python3 scripts/send_telegram.py
                            '''
                        }
                    }
                } catch (err) {
                    echo "Telegram notification failed: ${err.message}"
                }
            }
        }
    }
}