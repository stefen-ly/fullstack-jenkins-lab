pipeline {
    agent { label 'docker-ready' }

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        DEFAULT_EMAIL_TO = 'vanlythouern51@gmail.com'
    }

    parameters {
        booleanParam(name: 'DEPLOY_LOCAL', defaultValue: false,
                     description: 'Deploy containers on the Jenkins agent host (localhost:8088)')
        booleanParam(name: 'SIMULATE_FAILURE', defaultValue: false,
                     description: 'Force a failure to test FAILURE notifications')
        string(name: 'EMAIL_TO', defaultValue: '',
               description: 'Email address for SUCCESS/FAILURE notifications')
    }

    stages {
        stage('Checkout Git') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Check Build Agent') {
            steps {
                sh '''
                    set -eu
                    docker version >/dev/null
                    docker compose version
                    python3 --version
                    curl --version | head -n 1
                '''
            }
        }

        stage('Build + Test Backend and Frontend') {
            steps {
                // Both Dockerfiles run real automated tests while building.
                sh 'docker compose build'
            }
        }

        stage('Optional Failure Demo') {
            when { expression { return params.SIMULATE_FAILURE } }
            steps { error('Intentional failure to demonstrate notifications') }
        }

        stage('Deploy on Agent Host') {
            when { expression { return params.DEPLOY_LOCAL } }
            steps {
                sh '''
                    set -eu
                    docker compose up -d --no-build --remove-orphans
                    curl -fsS --retry 15 --retry-delay 2 --retry-connrefused http://127.0.0.1:8088/api/health
                    curl -fsS http://127.0.0.1:8088/api/tasks >/dev/null
                    echo 'Frontend: http://127.0.0.1:8088/'
                '''
            }
        }

        stage('Archive Build Summary') {
            steps {
                writeFile file: 'ci-summary.txt', text:
                    "Job: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nCommit: ${env.GIT_COMMIT ?: 'unknown'}\n"
                archiveArtifacts artifacts: 'ci-summary.txt', fingerprint: true
            }
        }
    }

    post {
        always {
            script {
                String status = currentBuild.currentResult
                String recipient = (params.EMAIL_TO ?: '').trim()
                String summary = "Jenkins ${status} | ${env.JOB_NAME} #${env.BUILD_NUMBER}"
                String bodyText = "Status: ${status}\nJob: ${env.JOB_NAME}\nBuild: #${env.BUILD_NUMBER}\nURL: ${env.BUILD_URL}\n"

                // One notification failure should not change the build result.
                if (recipient) {
                    try {
                        emailext(to: recipient, subject: summary,
                                 body: bodyText, attachLog: true)
                        echo 'Email notification requested.'
                    } catch (err) {
                        echo "Email notification failed (${err.getClass().getSimpleName()})."
                    }
                } else {
                    echo 'Email skipped: set EMAIL_TO parameter.'
                }

                try {
                    withCredentials([
                        string(credentialsId: 'telegram-bot-token', variable: 'TELEGRAM_BOT_TOKEN'),
                        string(credentialsId: 'telegram-chat-id', variable: 'TELEGRAM_CHAT_ID')
                    ]) {
                        withEnv(["NOTIFY_STATUS=${status}"]) {
                            sh(label: 'Telegram notification', script: '''
                                set +x
                                python3 scripts/send_telegram.py
                            ''')
                        }
                    }
                } catch (err) {
                    echo "Telegram notification failed (${err.getClass().getSimpleName()})."
                }
            }
        }
    }
}
