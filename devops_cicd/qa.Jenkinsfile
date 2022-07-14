def p_env = 'QA'
def git_url = 'http://git.neebal.com/hygge/hygge-ev-backend-python.git'
def git_branch = 'quality'
def email_body = 'Hygge EV Server Deployment'
def email_subject = 'Hygge EV QA Server Deployment'
def skipStage = false
def sonar_report = 'ERROR'
def SERVICE_MAIL_ID = 'ithelpdesk@neebal.com'

pipeline
{
    agent
    {
        label 'slave1'
    }
    options 
    {
        buildDiscarder(logRotator(numToKeepStr: '7'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }
    environment
    {
        SCANNER_HOME = tool name: 'sonar-scanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
    }
    parameters
    {
        string(name: 'build_id')
        string(name: 's3_path')
        choice(name: 'qualitygate_skip', choices: 'no\nyes')
        string(name: 'email_list')
        string(name: 'custom_params')
    }
    stages
    {
        stage('Initialization')
        {
            steps
            {
                script
                {
                    FAILED_STAGE = env.STAGE_NAME
                    if ("${s3_path}" == '')
                    {
                        INIT_FAILURE = 's3_path'
                        error 's3 path not provided'
                    }
                    if ("${custom_params}" != '') {
                    sh 'echo ${custom_params} > params.txt'
                    git_branch = sh(returnStdout: true, script: "cat params.txt | grep branch | cut -f2 -d'='").trim()
                    }
                }
            }
        }
        stage('Prebuild Notification')
        {
            steps
            {
                script {
                    FAILED_STAGE = env.STAGE_NAME
                }
                sh """
                cp /home/jenkins/email-templates/deploy/pre-build.html $WORKSPACE 
                sed -i 's/\$EMAIL_BODY/${email_body} pipeline has started/g' pre-build.html
                sed -i 's/\$ENV/${p_env}/g' pre-build.html
                sed -i 's/BUILD_TIMESTAMP/$BUILD_TIMESTAMP/g' pre-build.html
                sed -i 's/\$BUILD_NUMBER/$BUILD_NUMBER/g' pre-build.html
                sed -i 's/\$BUILD_STATUS/ONGOING/g' pre-build.html
                sed -i 's/\$TIME/60/g' pre-build.html
                sed -i 's/\$SERVICE_MAIL_ID/${SERVICE_MAIL_ID}/g' pre-build.html
                sed -i 's/\$COPY_RIGHT_YEAR/2021-2022/g' pre-build.html
                """
                emailext body: '${FILE,path="pre-build.html"}', subject: "${email_subject} Pipeline Started" , to: "\$email_list"
                sh "rm -rf pre-build.html"
            }
        }
        stage('Git Checkout')
        {
            when 
            {
                expression 
                {
                    checkout = !("${git_branch}" == 'quality')
                    return checkout;
                }
            }
            steps
            {
                script {
                    FAILED_STAGE = env.STAGE_NAME
                }
                git branch: "${git_branch}" , credentialsId: 'git', url: "${git_url}"
            }     
        }
        stage('Build')
        {
            steps
            {
                script {
                    FAILED_STAGE = env.STAGE_NAME
                }
                sh """
                rm -rf artifacts
                mkdir -p artifacts
                zip -r artifacts/hygge-ev-backend-python-qa.zip . -x '.git*' -x 'artifacts*'
                scp -o StrictHostKeyChecking=no artifacts/hygge-ev-backend-python-qa.zip hygge-ev-user@15.207.53.80:.
                """
            }
        }
        stage('SonarQube Static Code Analysis')
        {
            when 
            {
                expression 
                {
                    sonar = !(git_branch ==~ /_*([a-zA-Z0-9\W_&&[^\s]]*)dev_*([a-zA-Z0-9\W_&&[^\s]]*)/);
                    return sonar
                }
            }
            steps
            {
                script 
                {
                    FAILED_STAGE = env.STAGE_NAME
                    withSonarQubeEnv('sonarqube') 
                    {
                        //def temp_job_name = JOB_NAME.replaceAll('/','-')
                        sh "${SCANNER_HOME}/bin/sonar-scanner -Dsonar.sourceEncoding=UTF-8 -Dsonar.java.binaries=/usr/bin -Dsonar.sources=${WORKSPACE} -Dsonar.exclusions=/devops_cicd/** -Dsonar.projectKey=${JOB_BASE_NAME}-${git_branch};"
                        //sh "/opt/apache-maven-3.3.9/bin/mvn clean org.jacoco:jacoco-maven-plugin:prepare-agent install -Dmaven.test.failure.ignore=true sonar:sonar -Dsonar.projectKey=UPL-Udaan-Server-QA -Dsonar.projectName=UPL-Udaan-Server-QA -Dsonar.exclusions='target/**' -Dsonar.sourceEncoding=UTF-8;"
                        //sonarqube job status wait
                        withCredentials([usernamePassword(credentialsId: 'sonarqube_admin_user', usernameVariable: 'uname' , passwordVariable: 'upass')]) 
                        {
                            sh """
                            cd .scannerwork
                            #cd target/sonar
                            sonar_job_url=\$(cat report-task.txt | grep ceTaskUrl | awk -F 'ceTaskUrl=' '{print \$NF}')
                            while(true)
                            do
                                sonar_job_status=\$(curl -s --user "\$uname:\$upass" \$sonar_job_url | awk -F '"status":' '{print \$NF}' | cut -d ',' -f1 | sed 's/"//g')
                                sleep 10
                                if [ "\$sonar_job_status" != 'IN_PROGRESS' ]
                                then
                                echo "sonar job completed"
                                exit
                                fi
                            done
                            """
                        }
                    }
                    def qualitygate = waitForQualityGate()
                    sonar_report = qualitygate.status
                }
            }
        }
        stage('SonarQube Quality Gate')
        {
            when 
            {
                expression 
                {
                    sonar = !(git_branch ==~ /_*([a-zA-Z0-9\W_&&[^\s]]*)dev_*([a-zA-Z0-9\W_&&[^\s]]*)/);
                    quality = !(env.qualitygate_skip == 'yes')
                    return sonar && quality;
                }
            }
            steps
            {
                script
                {
                    FAILED_STAGE = env.STAGE_NAME
                    if (sonar_report != 'OK') 
                    {
                        error "Pipeline aborted due to quality gate failure: ${sonar_report}"
                    }
                }
            }
        }
        stage('Create Docker Image')
        {
            when
            {
                expression
                {
                    return skipStage;
                }
            }
            steps
            {
                sh 'echo Skipped'
            }
        }
        stage('Deploy')
        {
            steps
            {
                script {
                    FAILED_STAGE = env.STAGE_NAME
                }
                sh '''
                ssh -o StrictHostKeyChecking=no hygge-ev-user@15.207.53.80 <<'EOF'
                process=$(ps -ef | grep '8003' | grep -v 'grep' | awk '{print$2}' | wc -l)
                if [ "$process" -gt 1 ]
                then
                {
                kill -9 $(ps -ef | grep '8003' | grep -v 'grep' | awk '{print$2}')
                }
                fi
                mv ~/application-qa/server.log ~/logs-backup/server_qa_$(date +"%Y%m%d_%H%M%S").log
                rm -rf ~/application-qa/*
                unzip -o ~/hygge-ev-backend-python-qa.zip -d ~/application-qa/hygge-ev-backend-python/
                #pip install -r ~/application-qa/hygge-ev-backend-python/requirements.txt
                export JENKINS_NODE_COOKIE=dontKillMe
                cd ~/application-qa/hygge-ev-backend-python/
                /usr/bin/nohup /home/hygge-ev-user/.pyenv/shims/gunicorn app.main:application -b 0.0.0.0:8003 --env APP_ENV=qa > ~/application-qa/server.log &
                exit 0
                EOF
                '''
            }
        }
        stage('Upload Build Artifacts')
        {
            steps
            {
                script {
                    FAILED_STAGE = env.STAGE_NAME
                }
                sh """
                /usr/local/bin/aws --profile karma s3 cp artifacts/ 's3://${s3_path}' --recursive --quiet
                """
                archiveArtifacts artifacts: 'artifacts/*.zip', onlyIfSuccessful: true
            }
        }
        stage('Smoke Testing')
        {
            when
            {
                expression
                {
                    return skipStage;
                }
            }
            steps
            {
                sh 'echo Skipped'
            }
        }
        stage('Vulnerability Test Suite')
        {
            when
            {
                expression
                {
                    return skipStage;
                }
            }
            steps
            {
                sh 'echo Skipped'
            }
        }
        stage('Dynamic Code Analysis')
        {
            when
            {
                expression
                {
                    return skipStage;
                }
            }
            steps
            {
                sh 'echo Skipped'
            }
        }
        stage('File Defects Against Story')
        {
            when
            {
                expression
                {
                    return skipStage;
                }
            }
            steps
            {
                sh 'echo Skipped'
            }
        }
    }
    post
    {
        always
        {
            sh """
            cp /home/jenkins/email-templates/deploy/post-build.html $WORKSPACE 
            sed -i -- 's/\$EMAIL_BODY/${email_subject} pipeline has been completed/g' post-build.html
            sed -i -- 's/\$ENV/${p_env}/g' post-build.html
            sed -i -- "s/BUILD_TIMESTAMP/$BUILD_TIMESTAMP/g" post-build.html
            sed -i -- 's/\$TIME/60/g' post-build.html
            sed -i -- 's/\$SERVICE_MAIL_ID/${SERVICE_MAIL_ID}/g' post-build.html
            sed -i -- 's/\$COPY_RIGHT_YEAR/2021-2022/g' post-build.html
            """
            emailext body: '${FILE,path="post-build.html"}', subject: "${email_subject} Pipeline Completed", to: "\$email_list"
            sh "rm -rf post-build.html"         

            sh """
            if [ ! -z "${build_id}" ]
            then
            aws --profile karma sqs send-message\
            --queue-url https://sqs.ap-south-1.amazonaws.com/070290473916/KARMA-BUILD-STATUS-PROD\
            --message-body '"${BUILD_URL}"'\
            --delay-seconds 5\
            --message-attributes '{ "build_id":{ "DataType":"String","StringValue":"${build_id}" }, "data":{ "DataType":"String","StringValue":"${BUILD_URL}"}, "type":{ "DataType":"String","StringValue":"BUILD_STATUS"} }'
            fi
            """
        }
        success
        {
            script {
                currentBuild.description = "Build success"
            }
        }
        unsuccessful 
        {
            script
            {   
                if("${FAILED_STAGE}" == 'Initialization')
                {
                    if(INIT_FAILURE == 's3_path')
                    {
                        currentBuild.description = "s3 path not provided"
                    }
                }
                else {
                currentBuild.description = "${currentBuild.result} at ${FAILED_STAGE} stage"
                }
            }
        }
    }
}