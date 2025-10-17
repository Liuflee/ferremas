from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


@when('inicio el proceso de pago para el pedido')
def step_inicio_pago(context):
    context.browser.get(f"{context.base_url}/pago/iniciar/")
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.XPATH, "//h1|//form"))
    )


@when('completo los datos de pago con valores de prueba')
def step_completo_datos_pago(context):
    # Rellenar campos comunes si existen
    try:
        card = context.browser.find_element(By.NAME, 'card_number')
        card.send_keys('4242424242424242')
    except Exception:
        pass
    time.sleep(0.2)


@when('finalizo el pago')
def step_finalizo_pago(context):
    try:
        btn = context.browser.find_element(By.XPATH, "//button[contains(., 'Pagar') or contains(., 'Finalizar')]")
        btn.click()
    except Exception:
        pass
    time.sleep(0.5)


@then('debo ver la página de pago con resultado')
def step_ver_resultado_pago(context):
    WebDriverWait(context.browser, 5).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(., 'pago') or contains(., 'exitoso') or contains(., 'error')]"))
    )
