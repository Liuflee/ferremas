import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferremas.settings')
django.setup()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
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
    
    # Inicializar WebDriver con más estabilidad
    service = Service(ChromeDriverManager().install())
    context.browser = webdriver.Chrome(service=service, options=chrome_options)
    context.browser.implicitly_wait(10)
    
    # URL base de la aplicación
    context.base_url = os.environ.get('BASE_URL', 'http://localhost:8000')
    
    # Limpiar estado del navegador
    context.browser.delete_all_cookies()
    context.browser.get(context.base_url)
    
    # Crear datos de prueba
    setup_test_data()


def before_step(context, step):
    """Se ejecuta antes de cada paso"""
    try:
        # Intentar cerrar cualquier overlay que pueda interferir con clicks
        from features.steps.usuario_steps import _close_overlays
        _close_overlays(context)
    except Exception:
        pass

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
    """Crear datos de prueba: grupos, usuarios y productos"""
    # Crear grupos si no existen
    grupos = {}
    for grupo_nombre in ['Bodeguero', 'Vendedor', 'Contador']:
        grupo, _ = Group.objects.get_or_create(name=grupo_nombre)
        grupos[grupo_nombre] = grupo
    
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
    
    # Crear usuario cliente de prueba
    if not User.objects.filter(username='cliente1').exists():
        cliente = User.objects.create_user(
            username='cliente1',
            email='cliente1@test.com',
            password='Pass123!',
            first_name='Cliente',
            last_name='Test'
        )
        print(f"✓ Usuario cliente creado: {cliente.username}")

    # Crear usuario vendedor rcastro
    if not User.objects.filter(username='rcastro').exists():
        vendedor = User.objects.create_user(
            username='rcastro',
            email='rcastro@ferremas.cl',
            password='vendedor123',
            first_name='Roberto',
            last_name='Castro'
        )
        vendedor.groups.add(grupos['Vendedor'])
        print(f"✓ Usuario vendedor creado: {vendedor.username}")

    # Crear usuario bodeguero
    if not User.objects.filter(username='jperez').exists():
        bodeguero = User.objects.create_user(
            username='jperez',
            email='jperez@ferremas.cl',
            password='bodega123',
            first_name='Juan',
            last_name='Pérez'
        )
        bodeguero.groups.add(grupos['Bodeguero'])
        print(f"✓ Usuario bodeguero creado: {bodeguero.username}")

    # Crear usuario contador
    if not User.objects.filter(username='mlopez').exists():
        contador = User.objects.create_user(
            username='mlopez',
            email='mlopez@ferremas.cl',
            password='contador123',
            first_name='María',
            last_name='López'
        )
        contador.groups.add(grupos['Contador'])
        print(f"✓ Usuario contador creado: {contador.username}")
    
    # Crear productos de prueba si no existen
    from tienda.models import Producto, PrecioHistorico
    from django.utils import timezone
    if not Producto.objects.filter(nombre='Martillo Pro').exists():
        producto = Producto.objects.create(
            nombre='Martillo Pro',
            descripcion='Martillo profesional de acero',
            stock=20,
            categoria='herramientas_manuales',
            imagen='productos/martillo.jpg',
            activo=True
        )
        # Crear precio histórico para el producto
        PrecioHistorico.objects.create(
            producto=producto,
            fecha=timezone.now(),
            valor=9990
        )
        print("✓ Productos de prueba creados con precios")
