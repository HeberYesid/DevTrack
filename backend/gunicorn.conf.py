"""
Configuración de Gunicorn para DevTrack Backend
Servidor WSGI para producción
"""
import multiprocessing
import os

# ==============================================
# Server Socket
# ==============================================
bind = "0.0.0.0:8000"
backlog = 2048

# ==============================================
# Worker Processes
# ==============================================
# Número de workers: limitado para entornos de producción con recursos compartidos
# Railway/Heroku recomiendan 2-4 workers para planes básicos
workers = int(os.getenv("WEB_CONCURRENCY", "4"))  # Default: 4 workers
worker_class = "sync"
worker_connections = 1000
max_requests = 1000  # Reiniciar workers después de N requests (previene memory leaks)
max_requests_jitter = 50  # Añade aleatoriedad para evitar reinicios simultáneos
timeout = 30
keepalive = 2

# ==============================================
# Logging
# ==============================================
accesslog = "-"  # Log a stdout
errorlog = "-"   # Log a stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")  # debug, info, warning, error, critical
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ==============================================
# Process Naming
# ==============================================
proc_name = "devtrack-backend"

# ==============================================
# Server Mechanics
# ==============================================
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# ==============================================
# SSL (descomentar si se necesita HTTPS directo)
# ==============================================
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# ==============================================
# Server Hooks (opcional)
# ==============================================
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Gunicorn está iniciando...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("🔄 Gunicorn está recargando...")

def when_ready(server):
    """Called just after the server is started."""
    print("✅ Gunicorn está listo para aceptar conexiones")
    print(f"📊 Workers: {workers}")
    print(f"🔗 Bind: {bind}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("👋 Gunicorn se está deteniendo...")
