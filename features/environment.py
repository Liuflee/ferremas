import os
import django
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferremas.settings')
django.setup()


from django.contrib.auth.models import User, Group


def before_all(context):
    """Se ejecuta una vez antes de todas las pruebas"""
    print("=" * 70)
    print("  INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - FERREMÁS")
    print("  Sistema de Gestión de Usuarios")
    print("=" * 70)

def before_scenario(context, scenario):
    """Se ejecuta antes de cada escenario"""
    # Configurar opciones de Chrome
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Descomentar para modo sin interfaz
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Inicializar WebDriver
    service = Service(ChromeDriverManager().install())
    context.browser = webdriver.Chrome(service=service, options=chrome_options)
    context.browser.implicitly_wait(10)
    
    # URL base de la aplicación
    context.base_url = 'http://localhost:8000'
    
    # Crear datos de prueba
    setup_test_data()

def after_scenario(context, scenario):
    """Se ejecuta después de cada escenario"""
    # Capturar screenshot si el escenario falló
    if scenario.status == "failed":
        import os
        os.makedirs('reports/screenshots', exist_ok=True)
        screenshot_name = f"reports/screenshots/error_{scenario.name.replace(' ', '_')}.png"
        context.browser.save_screenshot(screenshot_name)
        print(f"Screenshot guardado: {screenshot_name}")
    
    # Cerrar navegador
    if hasattr(context, 'browser'):
        context.browser.quit()

def after_all(context):
    """Se ejecuta una vez después de todas las pruebas"""
    print("=" * 70)
    print("  SUITE DE PRUEBAS FINALIZADA")
    print("=" * 70)

def setup_test_data():
    """Crear datos de prueba: grupos y usuario admin"""
    # Crear grupos si no existen
    for grupo_nombre in ['Bodeguero', 'Vendedor', 'Contador']:
        Group.objects.get_or_create(name=grupo_nombre)
    
    # Crear usuario administrador de prueba
    if not User.objects.filter(username='admin_test').exists():
        admin = User.objects.create_superuser(
            username='admin_test',
            email='admin@ferremas.cl',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            is_staff=True
        )
        print(f"✓ Usuario administrador creado: {admin.username}")
