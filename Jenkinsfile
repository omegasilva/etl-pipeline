pipeline {
    agent any
    // If you prefer Docker:
    // agent {
    //     docker {
    //         image 'python:3.11-slim'
    //         args '-u root'
    //     }
    // }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Target environment for ETL run'
        )
        booleanParam(
            name: 'FULL_RELOAD',
            defaultValue: false,
            description: 'If true, perform a full reload. If false, incremental load.'
        )
        string(
            name: 'RUN_DATE',
            defaultValue: '',
            description: 'Optional run date (YYYY-MM-DD). Leave empty for “today”.'
        )
    }

    environment {
        // Simple text/file/secret credentials
        SRC_DB_DSN       = 'src-db-dsn-secret'     // e.g. postgres://...
        DW_DB_DSN        = 'dw-db-dsn-secret'     // e.g. warehouse DSN
        // For things like AWS, Snowflake, etc., add more here.
        // Example:
        // SNOWFLAKE_CREDS = credentials('snowflake-secret')
    }

    triggers {
        // Daily at 01:00
        cron('H 1 * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 --version || exit 1
                    if [ ! -d "venv" ]; then
                      python3 -m venv venv
                    fi
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r etl/requirements.txt
                '''
            }
        }

        stage('Extract') {
            steps {
                sh '''
                    set -e
                    . venv/bin/activate

                    RUN_DATE_ARG=${RUN_DATE:-$(date +%F)}

                    echo "Running EXTRACT for ENVIRONMENT=$ENVIRONMENT FULL_RELOAD=$FULL_RELOAD RUN_DATE=$RUN_DATE_ARG"

                    python etl/extract.py \
                      --env "$ENVIRONMENT" \
                      --full-reload "$FULL_RELOAD" \
                      --run-date "$RUN_DATE_ARG" \
                      --src-dsn "$SRC_DB_DSN" \
                      --output-dir "data/raw/$RUN_DATE_ARG"
                '''
            }
        }

        stage('Validate Extract') {
            steps {
                sh '''
                    echo "Running Validate Extract!!!"
                '''
            }
        }

        stage('Transform') {
            steps {
                sh '''
                    set -e
                    . venv/bin/activate

                    RUN_DATE_ARG=${RUN_DATE:-$(date +%F)}

                    echo "Running TRANSFORM for $RUN_DATE_ARG"

                    python etl/transform.py \
                      --env "$ENVIRONMENT" \
                      --full-reload "$FULL_RELOAD" \
                      --run-date "$RUN_DATE_ARG" \
                      --src-dsn "$SRC_DB_DSN" \
                      --output-dir "data/raw/$RUN_DATE_ARG"
                '''
            }
        }

        stage('Validate Transform') {
            steps {
                sh '''
                    echo "Running Validate Extract"
                '''
            }
        }

        stage('Load') {
            steps {
                sh '''
                    set -e
                    . venv/bin/activate

                    RUN_DATE_ARG=${RUN_DATE:-$(date +%F)}

                    echo "Running LOAD for $RUN_DATE_ARG"

                    python etl/load.py \
                      --env "$ENVIRONMENT" \
                      --full-reload "$FULL_RELOAD" \
                      --run-date "$RUN_DATE_ARG" \
                      --src-dsn "$SRC_DB_DSN" \
                      --output-dir "data/raw/$RUN_DATE_ARG"
                '''
            }
        }

        stage('Data Quality Checks') {
            steps {
                sh '''
                    set -e
                    . venv/bin/activate

                    RUN_DATE_ARG=${RUN_DATE:-$(date +%F)}

                    echo "Running DATA QUALITY for $RUN_DATE_ARG"

                    if [ -f etl/data_quality.py ]; then
                      python etl/data_quality.py \
                      --env "$ENVIRONMENT" \
                      --full-reload "$FULL_RELOAD" \
                      --run-date "$RUN_DATE_ARG" \
                      --src-dsn "$SRC_DB_DSN" \
                      --output-dir "data/raw/$RUN_DATE_ARG"
                    else
                      echo "No data_quality.py found, skipping."
                    fi
                '''
            }
        }

    }

    post {
        always {
            script {
                // Allocate a node so we have a FilePath/workspace
                node {
                    archiveArtifacts artifacts: 'data/**/*, logs/**/*', allowEmptyArchive: true
                }
            }
        }
        success {
            echo 'ETL pipeline completed successfully.'
            // Add Slack/email/etc. here if you want
        }
        failure {
            echo 'ETL pipeline FAILED.'
            // e.g. slackSend, emailext, etc.
        }
    }
}
