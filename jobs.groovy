
pipelineJob('jcasc-github-pipeline') {

    description(
        'Pipeline loaded from GitHub and created using JCasC + Job DSL'
    )

    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url(
                            'https://github.com/stefen-ly/fullstack-jenkins-lab.git'
                        )
                    }

                    branch('*/main')
                }
            }

            scriptPath('Jenkinsfile.jcasc')

            lightweight()
        }
    }
}

