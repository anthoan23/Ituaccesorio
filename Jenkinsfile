// Pipeline CI/CD para Ituaccesorio
// Flujo: análisis estático → levantar entorno de prueba → correr pruebas
//        → (si todas pasan) construir imagen → despliegue (solo main)
// La limpieza del entorno de prueba corre SIEMPRE al final, pase o falle.

pipeline {
    agent {
        node {
            // Workspace en ruta compartida host/contenedor: el daemon del host
            // resuelve los bind mounts, así que el checkout debe existir en
            // /home/anthoan/jenkins_ws en ambos lados (ver docker-compose.jenkins.yml)
            label 'built-in'
            customWorkspace '/home/anthoan/jenkins_ws'
        }
    }

    options {
        disableConcurrentBuilds()                     // los puertos 3317 no pueden chocar entre builds
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        PY       = 'python:3.12-slim'                 // misma base que el Dockerfile de la app
        WEB_PORT = '127.0.0.1:5010'                   // prod en 5010: el 5000 es del stack de desarrollo
    }

    stages {
        stage('Análisis estático (bandit)') {
            steps {
                sh '''#!/bin/bash
                docker run --rm -v "$PWD":/app -w /app \
                  -v jenkins_pip_cache:/root/.cache/pip \
                  ${PY} sh -c "pip install -q bandit && \
                  bandit -r . --exclude ./.git,./.venv -f html -o reporte_bandit.html || true"
                '''
            }
            post {
                always {
                    publishHTML(target: [
                        reportDir: '.',
                        reportFiles: 'reporte_bandit.html',
                        reportName: 'Bandit (seguridad)',
                        allowMissing: true,
                        keepAll: true, alwaysLinkToLastBuild: true])
                }
            }
        }

        stage('Levantar entorno de prueba') {
            steps {
                // Stack completo de prueba (web + las 2 MySQL): el web queda en 127.0.0.1:5001
                // y las BD en 127.0.0.2:3317 / 127.0.0.3:3317. tmpfs => BD limpias del seed.
                sh 'docker compose --env-file .env.test -p ituaccesorio_test -f docker-compose.test.yml up -d --wait'
            }
        }

        stage('Correr las pruebas') {
            steps {
                // --network host: el conftest de integración carga .env.test con override=True
                // y conecta a 127.0.0.2:3317 (las IPs del host); las de humo piden 127.0.0.1:5001.
                sh '''#!/bin/bash
                docker run --rm --network host --env-file .env.test \
                  -v "$PWD":/app -w /app \
                  -v jenkins_pip_cache:/root/.cache/pip \
                  ${PY} sh -c "pip install -q -r requirements.txt -r requirements-dev.txt && \
                  pytest 'tests/pruebas unitarias' -q --junitxml=reporte_unitarias.xml && \
                  pytest 'tests/pruebas de integracion' -q --junitxml=reporte_integracion.xml && \
                  pytest 'tests/pruebas de humo' -q --junitxml=reporte_humo.xml"
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reporte_*.xml'
                }
            }
        }

        stage('Construcción de imagen') {
            steps {
                // Solo llega aquí si TODAS las pruebas pasaron
                sh 'docker build -t ituaccesorio:${BUILD_NUMBER} .'
            }
        }

        stage('Despliegue en producción') {
            when { expression { env.GIT_BRANCH == 'origin/main' || env.BRANCH_NAME == 'main' } }
            steps {
                // .env real desde credencial (git no lo tiene)
                withCredentials([file(credentialsId: 'env-produccion', variable: 'ENV_FILE')]) {
                    sh 'cp "$ENV_FILE" .env'
                }
                // -p ituaccesorio_prod: volúmenes separados del desarrollo, los datos persisten
                sh 'docker compose -f docker-compose.prod.yml -p ituaccesorio_prod up -d --build'
                // Health check: 60 s de gracia
                sh '''#!/bin/bash
                for i in $(seq 1 30); do
                  if curl -fsS -o /dev/null http://127.0.0.1:5010/login; then
                    echo "App arriba en 127.0.0.1:5010"; exit 0
                  fi
                  sleep 2
                done
                echo "ERROR: la app no respondió en 60 s"; exit 1
                '''
            }
        }
    }

    post {
        always {
            // Elimina el entorno de prueba SIEMPRE (pase o falle): si una prueba falla y
            // los contenedores quedaran vivos, el siguiente build chocaría con el puerto 3317.
            // Las BD de prueba viven en tmpfs, así que borrarlas no pierde nada.
            sh 'docker compose --env-file .env.test -p ituaccesorio_test -f docker-compose.test.yml down -v --remove-orphans || true'
        }
        failure {
            // Notificación en consola (el correo se activa cuando configures SMTP)
            echo "Pipeline FALLÓ: revisa las etapas en rojo y el log de esta corrida"
            // Correo desactivado hasta configurar SMTP en Jenkins (Manage Jenkins →
            // System → E-mail Notification con contraseña de aplicación de Gmail).
            // Cuando esté listo, descomenta:
            // emailext(
            //     subject: "FALLÓ: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            //     body: "Revisa los logs aquí: ${env.BUILD_URL}",
            //     to: 'TU_CORREO@gmail.com')
        }
    }
}
