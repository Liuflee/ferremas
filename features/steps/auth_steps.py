from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def autenticar_usuario(context, username, password, tipo_usuario=""):
    """
    Función helper para autenticar usuarios
    """
    # Ir a la página de login si no estamos ya en ella
    if '/login/' not in context.browser.current_url:
        context.browser.get(context.base_url + '/login/')
    
    # Esperar a que los campos estén disponibles y completarlos
    user = context.browser.find_element(By.NAME, 'username')
    pwd = context.browser.find_element(By.NAME, 'password')
    user.clear()
    user.send_keys(username)
    pwd.clear()
    pwd.send_keys(password)
    
    # Click en el botón de login
    btn = context.browser.find_element(By.XPATH, "//button[contains(., 'Entrar') or contains(., 'Login') or contains(., 'Iniciar sesión')]")
    btn.click()
    time.sleep(0.5)
    
    # Verificar que estamos en la página correcta según el tipo de usuario
    if tipo_usuario:
        WebDriverWait(context.browser, timeout=10).until(
            lambda d: tipo_usuario.lower() in d.current_url.lower()
        )

@when('inserto usuario "{username}" y contraseña "{password}" y me autentico')
def step_login(context, username, password):
    autenticar_usuario(context, username, password)

@given('que me autentico como cliente con usuario "{username}" y contraseña "{password}"')
def step_impl(context, username, password):
    """
    Autenticar al usuario cliente con las credenciales proporcionadas
    """
    autenticar_usuario(context, username, password)

@given('estoy autenticado como usuario "{username}"')
def step_impl(context, username):
    """
    Autenticar usuarios del sistema (vendedor, bodeguero, contador) con sus credenciales predeterminadas
    """
    credentials = {
        'rcastro': ('rcastro', 'vendedor123', 'vendedor'),
        'jperez': ('jperez', 'bodega123', 'bodeguero'),
        'mlopez': ('mlopez', 'contador123', 'contador')
    }
    
    if username in credentials:
        user, password, tipo = credentials[username]
        autenticar_usuario(context, user, password, tipo)

@then('debo ver que estoy autenticado como "{username}"')
def step_ver_autenticado(context, username):
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.XPATH, f"//nav//*[contains(., '{username}')] | //a[contains(., '{username}')]"))
    )

@then('debería ver un mensaje de error de login')
def step_impl(context):
    """
    Verificar que se muestra un mensaje de error después de un intento de login fallido
    """
    error_message = WebDriverWait(context.browser, timeout=10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
    )
    assert error_message.is_displayed(), "No se muestra el mensaje de error"

@then('debería estar en la página de inicio de {tipo_usuario}')
def step_impl(context, tipo_usuario):
    """
    Verificar que estamos en la página correcta después del login
    """
    expected_urls = {
        'cliente': '/tienda/',
        'vendedor': '/vendedor/',
        'bodeguero': '/bodeguero/',
        'contador': '/contador/'
    }
    
    if tipo_usuario.lower() in expected_urls:
        expected_url = expected_urls[tipo_usuario.lower()]
        WebDriverWait(context.browser, timeout=10).until(
            lambda d: expected_url in d.current_url
        )
        assert expected_url in context.browser.current_url, \
            f"No estamos en la página correcta para {tipo_usuario}"
    

