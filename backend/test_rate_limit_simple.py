"""
Script de prueba simple para verificar el rate limiting.

Este script simula múltiples intentos de login para demostrar
que el rate limiting está funcionando correctamente.

Uso:
    python test_rate_limit_simple.py
"""
import requests
import json
import time
from datetime import datetime


def test_login_rate_limit():
    """Prueba el rate limiting en el endpoint de login"""
    url = "http://localhost:8000/api/auth/login/"
    
    # Datos de prueba (credenciales incorrectas intencionalmente)
    data = {
        "email": "test@example.com",
        "password": "wrongpassword",
        "turnstile_token": "test-token-for-testing"
    }
    
    print("=" * 60)
    print("🧪 PRUEBA DE RATE LIMITING - ENDPOINT LOGIN")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Límite esperado: 5 intentos por minuto")
    print("=" * 60)
    print()
    
    # Hacer 7 intentos para exceder el límite
    for i in range(1, 8):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Intento {i}...", end=" ")
        
        try:
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 429:
                print(f"❌ BLOQUEADO - {response.status_code}")
                print(f"           └─ Respuesta: {response.json()}")
                print()
                print("=" * 60)
                print("✅ ¡RATE LIMITING FUNCIONANDO CORRECTAMENTE!")
                print("=" * 60)
                return True
            else:
                print(f"✓ Permitido - {response.status_code}")
                if response.status_code in [400, 401]:
                    print(f"           └─ (Error de autenticación esperado)")
        
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: No se puede conectar al servidor")
            print("   Asegúrate de que el servidor Django esté corriendo:")
            print("   python manage.py runserver")
            return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
        
        # Pequeña pausa entre intentos
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print("⚠️ ADVERTENCIA: No se alcanzó el límite después de 7 intentos")
    print("   El rate limiting podría no estar configurado correctamente")
    print("=" * 60)
    return False


def test_register_rate_limit():
    """Prueba el rate limiting en el endpoint de registro"""
    url = "http://localhost:8000/api/auth/register/"
    
    print()
    print("=" * 60)
    print("🧪 PRUEBA DE RATE LIMITING - ENDPOINT REGISTER")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Límite esperado: 5 intentos por minuto")
    print("=" * 60)
    print()
    
    # Hacer 6 intentos
    for i in range(1, 7):
        data = {
            "email": f"test{i}@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "turnstile_token": "test-token"
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Intento {i}...", end=" ")
        
        try:
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 429:
                print(f"❌ BLOQUEADO - {response.status_code}")
                print(f"           └─ Respuesta: {response.json()}")
                print()
                print("=" * 60)
                print("✅ ¡RATE LIMITING EN REGISTER FUNCIONANDO!")
                print("=" * 60)
                return True
            else:
                print(f"✓ Permitido - {response.status_code}")
        
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
        
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print("⚠️ No se alcanzó el límite en register")
    print("=" * 60)
    return False


def main():
    """Función principal"""
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║     PRUEBA DE RATE LIMITING - DevTrack                ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("Este script verifica que el rate limiting esté activo")
    print("en los endpoints de autenticación.")
    print()
    input("Presiona ENTER para comenzar las pruebas...")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8000/api/")
        print("✓ Servidor Django detectado y corriendo")
        print()
    except:
        print("❌ ERROR: No se puede conectar a http://localhost:8000")
        print()
        print("Por favor, inicia el servidor Django:")
        print("  cd backend")
        print("  python manage.py runserver")
        print()
        return
    
    # Ejecutar pruebas
    login_ok = test_login_rate_limit()
    
    if login_ok:
        # Esperar un poco antes de probar register
        print()
        print("Esperando 3 segundos antes de la siguiente prueba...")
        time.sleep(3)
        register_ok = test_register_rate_limit()
    
    # Resumen final
    print()
    print("=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Login Rate Limit:    {'✅ PASS' if login_ok else '❌ FAIL'}")
    # print(f"Register Rate Limit: {'✅ PASS' if register_ok else '❌ FAIL'}")
    print("=" * 60)
    print()
    
    if login_ok:
        print("🎉 ¡Excelente! El rate limiting está funcionando correctamente.")
        print()
        print("💡 Próximos pasos:")
        print("   - Ejecutar pruebas completas: pytest backend/accounts/tests/test_ratelimit.py")
        print("   - Revisar documentación: backend/RATE_LIMITING_DOCS.md")
        print("   - Configurar Redis para producción")
    else:
        print("⚠️ Hay problemas con el rate limiting.")
        print()
        print("🔧 Soluciones:")
        print("   1. Verifica que django-ratelimit esté instalado")
        print("   2. Confirma que RATELIMIT_ENABLE=True en .env")
        print("   3. Revisa la configuración de CACHES en settings.py")
        print("   4. Reinicia el servidor Django")


if __name__ == "__main__":
    main()
