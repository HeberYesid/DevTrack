"""
Script para crear superuser en Railway mediante la API
"""
import requests
import sys

# Configuración
API_BASE_URL = "https://devtrack-production-2b1d.up.railway.app"
EMAIL = "heberyesid@devtrack.com"
PASSWORD = "TuPasswordSeguro123!"
FIRST_NAME = "Heber"
LAST_NAME = "Daza"

def create_superuser():
    """Intenta crear un superuser mediante registro y luego actualización directa en DB"""
    
    # Primero, intentar registrar el usuario
    print("🔄 Registrando usuario...")
    register_url = f"{API_BASE_URL}/api/accounts/register/"
    
    register_data = {
        "email": EMAIL,
        "password": PASSWORD,
        "password2": PASSWORD,
        "first_name": FIRST_NAME,
        "last_name": LAST_NAME,
        "role": "ADMIN",  # Intentar con rol ADMIN
        "turnstile_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Token dummy para testing
    }
    
    try:
        response = requests.post(register_url, json=register_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Usuario creado exitosamente!")
            print("\n⚠️  IMPORTANTE: Este usuario fue creado pero necesita ser promovido a superuser.")
            print("   Necesitarás acceder a Railway's database directamente para hacer:")
            print("   UPDATE accounts_customuser SET is_superuser=1, is_staff=1 WHERE email='heberyesid@devtrack.com';")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print("ℹ️  El usuario ya existe")
            return True
        else:
            print(f"❌ Error al crear usuario: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Creación de Superuser en Railway ===\n")
    create_superuser()
    print("\n=== Proceso completado ===")
