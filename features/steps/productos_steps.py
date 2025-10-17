from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException
import time


@given('estoy en el panel de productos')
def step_en_panel_productos(context):
    context.browser.get(f"{context.base_url}/adminpanel/productos/")
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Productos') or contains(., 'Panel de productos')]"))
    )


@given('existe un producto con id {pid} en el sistema')
def step_existe_producto(context, pid):
    # asumimos que el fixture o setup ya creó el producto
    context.browser.get(f"{context.base_url}/producto/{pid}/")
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".producto-detalle, .product-detail"))
    )


@given('existe un producto con nombre "{nombre}" en el sistema')
def step_existe_producto_nombre(context, nombre):
    # asumimos que el fixture ya creó el producto; verificamos que exista
    context.browser.get(f"{context.base_url}/catalogo/")
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.XPATH, f"//div[contains(@class,'producto') and contains(.,'{nombre}')]"))
    )


@when('activo el formulario para crear producto')
def step_activar_form_producto(context):
    btn = context.browser.find_element(By.XPATH, "//button[contains(., 'Crear producto') or contains(., 'Nuevo producto')]")
    btn.click()
    time.sleep(0.2)


@when('relleno los datos del producto:')
def step_rellenar_datos_producto(context):
    for row in context.table:
        campo = row['campo']
        valor = row['valor']
        if campo == 'activo':
            # Manejar checkbox
            try:
                checkbox = context.browser.find_element(By.NAME, 'activo')
                if valor.lower() == 'true' and not checkbox.is_selected():
                    checkbox.click()
                elif valor.lower() == 'false' and checkbox.is_selected():
                    checkbox.click()
                continue
            except:
                pass
        try:
            el = context.browser.find_element(By.NAME, campo)
            el.clear()
            el.send_keys(valor)
        except Exception:
            try:
                el = context.browser.find_element(By.ID, campo)
                el.clear()
                el.send_keys(valor)
            except Exception:
                pass

@when('relleno los datos de precio:')
def step_rellenar_precio(context):
    for row in context.table:
        campo = row['campo']
        valor = row['valor']
        try:
            el = context.browser.find_element(By.NAME, 'valor')  # PrecioHistorico.valor
            el.clear()
            el.send_keys(valor)
        except Exception:
            try:
                el = context.browser.find_element(By.NAME, 'precio')  # campo de precio en form
                el.clear()
                el.send_keys(valor)
            except Exception:
                pass

@then('el precio del producto "{nombre}" debe ser "{precio}"')
def step_verificar_precio(context, nombre, precio):
    precio_regex = precio.replace('$', r'\$').replace('.', r'\.')
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.XPATH, f"//td[contains(., '{nombre}')]/..//td[contains(., '{precio_regex}')]"))
    )


@when('presiono el botón de producto con texto "{texto}"')
def step_click_boton_producto(context, texto):
    el = context.browser.find_element(By.XPATH, f"//button[contains(., '{texto}')] | //a[contains(., '{texto}')]")
    el.click()
    time.sleep(0.3)


@then('debo ver el producto con nombre "{nombre}" en la lista')
def step_ver_producto_en_lista(context, nombre):
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.XPATH, f"//table//td[contains(., '{nombre}')]"))
    )


@when('busco el producto por nombre "{texto}"')
def step_buscar_producto(context, texto):
    try:
        inp = context.browser.find_element(By.NAME, 'q')
        inp.clear(); inp.send_keys(texto)
        btn = context.browser.find_element(By.XPATH, "//button[contains(., 'Buscar') or contains(., 'Search')]")
        btn.click()
    except Exception:
        # fallback: usar querystring
        context.browser.get(f"{context.base_url}/catalogo/?q={texto}")
    time.sleep(0.4)


@when('edito el producto con id {pid}')
def step_editar_producto(context, pid):
    context.browser.get(f"{context.base_url}/producto/{pid}/editar/")
    time.sleep(0.3)


@when('elimino el producto con id {pid}')
def step_eliminar_producto(context, pid):
    context.browser.get(f"{context.base_url}/producto/{pid}/eliminar/")
    try:
        btn = context.browser.find_element(By.XPATH, "//button[contains(., 'Confirmar') or contains(., 'Eliminar')]")
        btn.click()
    except Exception:
        pass
    time.sleep(0.4)
