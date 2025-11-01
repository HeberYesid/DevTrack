#!/usr/bin/env python
"""
Script para verificar las variables de entorno en Railway
Ejecutar desde Railway Shell o localmente para debug
"""
import os

print("=" * 60)
print("🔍 VERIFICACIÓN DE VARIABLES DE ENTORNO")
print("=" * 60)

# Variables críticas para la base de datos
db_vars = [
    'DATABASE_URL',
    'DB_NAME',
    'DB_USER', 
    'DB_PASSWORD',
    'DB_HOST',
    'DB_PORT',
    'MYSQLHOST',
    'MYSQLPORT',
    'MYSQLDATABASE',
    'MYSQLUSER',
    'MYSQLPASSWORD',
]

print("\n📊 VARIABLES DE BASE DE DATOS:")
print("-" * 60)
for var in db_vars:
    value = os.getenv(var)
    if value:
        # Ocultar contraseñas
        if 'PASSWORD' in var or 'SECRET' in var:
            display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
        else:
            display_value = value
        print(f"✅ {var:20s} = {display_value}")
    else:
        print(f"❌ {var:20s} = (no configurada)")

# Variables de Django
django_vars = [
    'DJANGO_SECRET_KEY',
    'DJANGO_DEBUG',
    'DJANGO_ALLOWED_HOSTS',
    'CORS_ALLOWED_ORIGINS',
]

print("\n⚙️  VARIABLES DE DJANGO:")
print("-" * 60)
for var in django_vars:
    value = os.getenv(var)
    if value:
        if 'SECRET' in var:
            display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
        else:
            display_value = value
        print(f"✅ {var:20s} = {display_value}")
    else:
        print(f"❌ {var:20s} = (no configurada)")

# Railway específicas
railway_vars = [
    'RAILWAY_ENVIRONMENT',
    'RAILWAY_PUBLIC_DOMAIN',
    'PORT',
]

print("\n🚂 VARIABLES DE RAILWAY:")
print("-" * 60)
for var in railway_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var:20s} = {value}")
    else:
        print(f"❌ {var:20s} = (no configurada)")

print("\n" + "=" * 60)
print("💡 RECOMENDACIONES:")
print("=" * 60)

database_url = os.getenv('DATABASE_URL')
has_individual_db = all([
    os.getenv('DB_HOST'),
    os.getenv('DB_NAME'),
    os.getenv('DB_USER')
])
has_mysql_vars = all([
    os.getenv('MYSQLHOST'),
    os.getenv('MYSQLDATABASE'),
    os.getenv('MYSQLUSER')
])

if database_url:
    print("✅ DATABASE_URL está configurada - Django la usará")
elif has_individual_db:
    print("✅ Variables DB_* están configuradas - Django las usará")
elif has_mysql_vars:
    print("⚠️  Variables MYSQL* están presentes pero Django necesita DB_* o DATABASE_URL")
    print("   Solución: Mapear MYSQL* → DB_* en Railway Variables")
else:
    print("❌ NO hay variables de base de datos configuradas")
    print("   Solución: Configurar DATABASE_URL=${{MySQL.DATABASE_URL}}")

print("=" * 60)
