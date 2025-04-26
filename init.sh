    #!/bin/bash

    echo "Создаю .env файл..."

    FERNET_KEY=$(openssl rand -base64 32)
    WEBSERVER_SECRET_KEY=$(openssl rand -hex 32)
    AIRFLOW_ADMIN_PASSWORD=$(openssl rand -hex 12)

    cat <<EOF > .env
    POSTGRES_USER=airflow
    POSTGRES_PASSWORD=airflow
    POSTGRES_DB=airflow

    FERNET_KEY=${FERNET_KEY}
    WEBSERVER_SECRET_KEY=${WEBSERVER_SECRET_KEY}

    AIRFLOW_ADMIN_USERNAME=admin
    AIRFLOW_ADMIN_FIRSTNAME=Admin
    AIRFLOW_ADMIN_LASTNAME=User
    AIRFLOW_ADMIN_EMAIL=admin@example.com
    AIRFLOW_ADMIN_PASSWORD=${AIRFLOW_ADMIN_PASSWORD}
    EOF

    echo ".env создан! Пароль администратора: ${AIRFLOW_ADMIN_PASSWORD}"

    echo "Собираю и запускаю docker-compose..."
    docker compose up --build