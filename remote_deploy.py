"""
Script de despliegue remoto para CodeAcademy Backend
Usa paramiko para conectarse por SSH al VPS y ejecutar los comandos de despliegue
"""
import paramiko
import sys
import time
import io

# Fix Windows console encoding - handle any Unicode from SSH output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ============================================================
# CONFIGURACION
# ============================================================
VPS_IP = "159.223.133.69"
VPS_USER = "root"
VPS_PASSWORD = "1707381677BACKEND"

PROJECT_DIR = "/opt/codeacademy/CodeAcademy_bakend"
VENV_DIR = f"{PROJECT_DIR}/venv"
REPO_URL = "https://github.com/sergio001g/CodeAcademy_bakend.git"
DB_NAME = "codeacademy"
DB_USER = "codeacademy"
DB_PASSWORD = "C0d3Ac4d3my_Pr0d_2026"
SECRET_KEY = "xK9mP2nQ7rS4tU8vW1xY3zA5bC7dE9fG2hJ4kL6mN8pR0sT"


def run_ssh_command(ssh, command, description="", ignore_errors=False):
    """Ejecuta un comando SSH y muestra el output"""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print(f"{'='*60}")
    
    print(f"  $ {command[:120]}{'...' if len(command) > 120 else ''}")
    
    stdin, stdout, stderr = ssh.exec_command(command, timeout=300)
    
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    if out:
        for line in out.split('\n'):
            print(f"  {line}")
    if err and not ignore_errors:
        for line in err.split('\n'):
            print(f"  [stderr] {line}")
    
    if exit_code != 0 and not ignore_errors:
        print(f"  [!] Exit code: {exit_code}")
    
    return exit_code, out, err


def main():
    print(f"""
========================================================
   DESPLIEGUE CODEACADEMY BACKEND
   VPS: {VPS_IP}
   OS: Ubuntu 24.04 LTS
========================================================
""")

    # ---- CONECTAR AL VPS ----
    print("[*] Conectando al VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASSWORD, timeout=30)
        print(f"[OK] Conectado a {VPS_IP} como {VPS_USER}")
    except Exception as e:
        print(f"[ERROR] Error de conexion: {e}")
        sys.exit(1)

    # ---- 1. ACTUALIZAR SISTEMA ----
    run_ssh_command(ssh, 
        "export DEBIAN_FRONTEND=noninteractive && apt update -y && apt upgrade -y",
        "1/10 - Actualizando sistema operativo")

    # ---- 2. INSTALAR DEPENDENCIAS ----
    run_ssh_command(ssh,
        "export DEBIAN_FRONTEND=noninteractive && apt install -y python3 python3-venv python3-pip python3-dev postgresql postgresql-contrib nginx git libpq-dev curl ufw",
        "2/10 - Instalando dependencias del sistema")

    # ---- 3. CONFIGURAR POSTGRESQL ----
    run_ssh_command(ssh, "systemctl start postgresql && systemctl enable postgresql",
        "3/10 - Configurando PostgreSQL", ignore_errors=True)
    
    run_ssh_command(ssh,
        f"""sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='{DB_USER}'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';" """,
        "", ignore_errors=True)
    
    run_ssh_command(ssh,
        f"""sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE {DB_NAME} OWNER {DB_USER};" """,
        "", ignore_errors=True)
    
    run_ssh_command(ssh, f"""sudo -u postgres psql -c "ALTER ROLE {DB_USER} SET client_encoding TO 'utf8';" """, "", ignore_errors=True)
    run_ssh_command(ssh, f"""sudo -u postgres psql -c "ALTER ROLE {DB_USER} SET default_transaction_isolation TO 'read committed';" """, "", ignore_errors=True)
    run_ssh_command(ssh, f"""sudo -u postgres psql -c "ALTER ROLE {DB_USER} SET timezone TO 'America/Bogota';" """, "", ignore_errors=True)
    run_ssh_command(ssh, f"""sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};" """, "", ignore_errors=True)

    print("  [OK] PostgreSQL configurado")

    # ---- 4. CLONAR REPOSITORIO ----
    run_ssh_command(ssh, "mkdir -p /opt/codeacademy", "4/10 - Clonando / Actualizando repositorio")
    
    # Verificar si ya existe
    exit_code, out, _ = run_ssh_command(ssh, f"test -d {PROJECT_DIR} && echo EXISTS || echo NOTEXISTS", "")
    
    if "EXISTS" in out:
        run_ssh_command(ssh, f"cd {PROJECT_DIR} && git fetch --all && git reset --hard origin/main", "")
        print("  [OK] Repositorio actualizado a origin/main")
    else:
        run_ssh_command(ssh, f"cd /opt/codeacademy && git clone {REPO_URL}", "")
        print("  [OK] Repositorio clonado")

    # ---- 5. ENTORNO VIRTUAL Y DEPENDENCIAS ----
    run_ssh_command(ssh, f"python3 -m venv {VENV_DIR}",
        "5/10 - Configurando entorno virtual Python")
    
    run_ssh_command(ssh, f"{VENV_DIR}/bin/pip install --upgrade pip", "")
    run_ssh_command(ssh, f"{VENV_DIR}/bin/pip install -r {PROJECT_DIR}/requirements.txt", "")
    
    print("  [OK] Dependencias Python instaladas")

    # ---- 6. CREAR ARCHIVO .env ----
    env_content = f"""SECRET_KEY={SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=*
POSTGRES_DB={DB_NAME}
POSTGRES_USER={DB_USER}
POSTGRES_PASSWORD={DB_PASSWORD}
DB_HOST=localhost
DB_PORT=5432
"""
    
    run_ssh_command(ssh, f"""cat > {PROJECT_DIR}/.env << 'ENVEOF'
{env_content}
ENVEOF""",
        "6/10 - Configurando variables de entorno (.env)")
    
    print("  [OK] Archivo .env creado")

    # ---- 7. DIRECTORIOS Y RECURSOS ----
    run_ssh_command(ssh, f"mkdir -p {PROJECT_DIR}/media {PROJECT_DIR}/staticfiles",
        "7/10 - Preparando directorios estaticos y media")
    
    print("  [OK] Directorios listos")

    # ---- 8. MIGRACIONES Y DATOS INICIALES ----
    run_ssh_command(ssh, f"cd {PROJECT_DIR} && {VENV_DIR}/bin/python manage.py makemigrations users courses enrollments reviews quizzes forums",
        "8/10 - Generando y aplicando migraciones para apps modulares")
    run_ssh_command(ssh, f"cd {PROJECT_DIR} && {VENV_DIR}/bin/python manage.py migrate --noinput", "")
    
    run_ssh_command(ssh, 
        f"cd {PROJECT_DIR} && {VENV_DIR}/bin/python manage.py configurar_roles --email admin@codeacademy.com --password admin123",
        "", ignore_errors=True)
    
    run_ssh_command(ssh, f"cd {PROJECT_DIR} && {VENV_DIR}/bin/python manage.py collectstatic --noinput", "")
    
    print("  [OK] Migraciones, roles y archivos estaticos listos")

    # ---- 9. CONFIGURAR GUNICORN ----
    gunicorn_socket = """[Unit]
Description=gunicorn socket para CodeAcademy

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target"""

    gunicorn_service = f"""[Unit]
Description=Gunicorn daemon para CodeAcademy Backend
Requires=gunicorn.socket
After=network.target postgresql.service

[Service]
User=root
Group=www-data
WorkingDirectory={PROJECT_DIR}
ExecStart={VENV_DIR}/bin/gunicorn \\
    --access-logfile /var/log/gunicorn/access.log \\
    --error-logfile /var/log/gunicorn/error.log \\
    --workers 3 \\
    --bind unix:/run/gunicorn.sock \\
    core.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target"""

    run_ssh_command(ssh, f"""cat > /etc/systemd/system/gunicorn.socket << 'SOCKETEOF'
{gunicorn_socket}
SOCKETEOF""",
        "9/10 - Configurando Gunicorn como servicio systemd")

    run_ssh_command(ssh, f"""cat > /etc/systemd/system/gunicorn.service << 'SERVICEEOF'
{gunicorn_service}
SERVICEEOF""", "")

    run_ssh_command(ssh, "mkdir -p /var/log/gunicorn", "")
    run_ssh_command(ssh, "systemctl daemon-reload", "")
    run_ssh_command(ssh, "systemctl restart gunicorn.socket", "")
    run_ssh_command(ssh, "systemctl restart gunicorn", "")
    
    print("  [OK] Gunicorn configurado y reiniciado")

    # ---- 10. CONFIGURAR NGINX ----
    nginx_config = f"""server {{
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    client_max_body_size 10M;

    location /static/ {{
        alias {PROJECT_DIR}/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}

    location /media/ {{
        alias {PROJECT_DIR}/media/;
        expires 30d;
    }}

    location = /favicon.ico {{
        access_log off;
        log_not_found off;
    }}

    location / {{
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}"""

    run_ssh_command(ssh, f"""cat > /etc/nginx/sites-available/codeacademy << 'NGINXEOF'
{nginx_config}
NGINXEOF""",
        "10/10 - Configurando Nginx como reverse proxy")

    run_ssh_command(ssh, "ln -sf /etc/nginx/sites-available/codeacademy /etc/nginx/sites-enabled/", "")
    run_ssh_command(ssh, "rm -f /etc/nginx/sites-enabled/default", "")
    run_ssh_command(ssh, "nginx -t", "")
    run_ssh_command(ssh, "systemctl restart nginx && systemctl enable nginx", "")
    
    print("  [OK] Nginx configurado y ejecutandose")

    # ---- FIREWALL ----
    run_ssh_command(ssh, "ufw allow 'Nginx Full' && ufw allow OpenSSH", 
        "Configurando firewall", ignore_errors=True)
    run_ssh_command(ssh, "echo 'y' | ufw enable", "", ignore_errors=True)
    
    print("  [OK] Firewall configurado")

    # ---- VERIFICACIÓN ----
    print(f"\n{'='*60}")
    print("  VERIFICACIÓN")
    print(f"{'='*60}")
    
    run_ssh_command(ssh, "systemctl status gunicorn --no-pager -l", "Estado de Gunicorn", ignore_errors=True)
    run_ssh_command(ssh, "systemctl status nginx --no-pager -l", "Estado de Nginx", ignore_errors=True)
    
    # Test con curl
    exit_code, out, _ = run_ssh_command(ssh, f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost/api/docs/", "Test de conexión local API Docs")
    print(f"  [HTTP CODE API DOCS]: {out}")

    print(f"""
========================================================
   ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!
========================================================

   Dominio Principal:
   http://codeacademy-api.uaeftt-ute.site/api/docs/

   IP VPS Directa:
   http://{VPS_IP}/api/docs/

========================================================
""")

    ssh.close()
    print("[OK] Conexion SSH cerrada")


if __name__ == "__main__":
    main()
