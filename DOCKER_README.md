# 🐳 DevTrack - Inicio Rápido con Docker

## ⚡ Quick Start

### 1. Prerequisitos
- Docker Desktop instalado y corriendo
- Al menos 4GB de RAM disponible

### 2. Configurar variables de entorno
```powershell
# Copiar archivo de ejemplo
Copy-Item .env.docker.example .env.docker

# Editar si es necesario (opcional en desarrollo)
notepad .env.docker
```

### 3. Iniciar en modo desarrollo
```powershell
.\scripts\docker-dev.ps1
```

**Listo!** 🎉 La aplicación estará disponible en:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs/

---

## 📋 Comandos Útiles

### Desarrollo
```powershell
.\scripts\docker-dev.ps1       # Iniciar desarrollo
.\scripts\docker-logs.ps1      # Ver logs
.\scripts\docker-test.ps1      # Ejecutar tests
.\scripts\docker-shell.ps1 backend  # Abrir shell en backend
```

### Producción
```powershell
.\scripts\docker-prod.ps1      # Iniciar producción
docker-compose ps              # Ver estado
docker-compose down            # Detener
```

### Limpieza
```powershell
.\scripts\docker-clean.ps1     # Limpiar contenedores
```

---

## 📚 Documentación Completa

Ver documentación detallada en:
- [Plan de Docker](./docs/DOCKER_PLAN.md)
- [Guía de Setup](./docs/DOCKER_SETUP.md) *(próximamente)*
- [Troubleshooting](./docs/DOCKER_TROUBLESHOOTING.md) *(próximamente)*
