from behave import when, then, given
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


@given('tengo productos en el catálogo')
def step_tengo_productos(context):
    # Asume que fixtures ya cargaron productos; simplemente vamos al catálogo
    context.browser.get(f"{context.base_url}/catalogo/")
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".producto, .product, .card"))
    )


@when('agrego el producto con id {producto_id} al carrito')
def step_agrego_producto_al_carrito(context, producto_id):
    context.browser.get(f"{context.base_url}/agregar-al-carrito/{producto_id}/")
    time.sleep(0.3)


@when('voy a la página del carrito')
def step_ir_carrito(context):
    context.browser.get(f"{context.base_url}/carrito/")
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#carrito, .cart, .carrito-list"))
    )


@then('debo ver {cantidad:d} items en el carrito')
def step_ver_items_carrito(context, cantidad):
    textos = context.browser.find_elements(By.XPATH, "//table//tr|//ul[contains(@class,'cart')]/li")
    assert len(textos) >= cantidad


@when('agrego multiples productos al carrito')
def step_agrego_varios(context):
    for row in context.table:
        pid = row['producto_id']
        context.browser.get(f"{context.base_url}/agregar-al-carrito/{pid}/")
        time.sleep(0.2)


@when('procedo al pago desde el carrito')
def step_procedo_pago(context):
    context.browser.get(f"{context.base_url}/pago/iniciar/")
    time.sleep(0.3)
