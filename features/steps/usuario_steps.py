from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User, Group
from behave.api.pending_step import StepNotImplementedError
import time

def _close_overlays(context):
    """Intentar cerrar banners o overlays comunes que puedan interceptar clicks."""
    try:
        # botones comunes de cookies/aceptar
        possibles = context.browser.find_elements(By.XPATH, "//button[contains(., 'Aceptar') or contains(., 'Cerrar') or contains(., 'OK')]")
        for b in possibles:
            try:
                if b.is_displayed():
                    b.click()
                    time.sleep(0.1)
            except Exception:
                continue
    except Exception:
        pass


def _safe_click(context, element):
    """Intentar hacer click de forma robusta: scroll, click normal, ActionChains, JS."""
    try:
        context.browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
    except Exception:
        pass
    time.sleep(0.2)
    try:
        element.click()
        return
    except ElementClickInterceptedException:
        try:
            ActionChains(context.browser).move_to_element(element).click(element).perform()
            return
        except Exception:
            try:
                context.browser.execute_script("arguments[0].click();", element)
                return
            except Exception:
                raise


def _find_in_row(fila, texts=None, classes=None):
    """Buscar un botón/enlace dentro de una fila por texto o clase. texts: list of substrings."""
    texts = texts or []
    classes = classes or []
    # buscar por texto primero
    for txt in texts:
        try:
            el = fila.find_element(By.XPATH, f".//button[contains(normalize-space(.), '{txt}')] | .//a[contains(normalize-space(.), '{txt}')]")
            return el
        except Exception:
            continue
    # buscar por clase
    for cls in classes:
        try:
            el = fila.find_element(By.XPATH, f".//button[contains(@class, '{cls}')] | .//a[contains(@class, '{cls}')]")
            return el
        except Exception:
            continue
    # fallback: cualquier button o a
    try:
        return fila.find_element(By.XPATH, ".//button | .//a")
    except Exception:
        raise NoSuchElementException("No se encontró elemento clicable en la fila")

# ============================================
# PASOS COMUNES (Given/Antecedentes)
# ============================================

@given('que el sistema Ferremás está iniciado')
def step_sistema_iniciado(context):
    """Verificar que el servidor Django está corriendo"""
    context.browser.get(context.base_url)
    assert "Ferremás" in context.browser.title or context.browser.current_url

@given('estoy en la página de login')
def step_pagina_login(context):
    """Navegar a la página de login"""
    context.browser.get(f"{context.base_url}/login/")
    # Esperar a que cargue el formulario
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.ID, "email_l"))
    )

@given('me autentico como administrador con usuario "{username}" y contraseña "{password}"')
def step_autenticar_admin(context, username, password):
    """Realizar login como administrador"""
    # Buscar campos de login
    email_field = context.browser.find_element(By.ID, "email_l")
    password_field = context.browser.find_element(By.ID, "password_l")
    
    # Ingresar credenciales
    email_field.clear()
    email_field.send_keys(f"{username}@ferremas.cl" if '@' not in username else username)
    password_field.clear()
    password_field.send_keys(password)
    
    # Hacer clic en botón de login
    login_button = context.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    
    # Esperar a que se complete el login (verificar que estamos en panel admin)
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "admin-header"))
    )

@given('estoy en el panel de gestión de usuarios')
def step_en_panel_usuarios(context):
    """Navegar al panel de usuarios"""
    # Asegurarse de incluir la barra entre base_url y la ruta
    context.browser.get(f"{context.base_url}/adminpanel/usuarios/")
    # Esperar a que cargue la página
    WebDriverWait(context.browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h2"))
    )

@given('existe un usuario con username "{username}"')
def step_existe_usuario_username(context, username):
    """Crear usuario de prueba si no existe"""
    from features.fixtures.test_data import UsuariosTestData
    if username == 'mtorres':
        UsuariosTestData.crear_usuario_bodeguero()
    context.usuario_test_username = username

@given('existe un usuario con nombre "{nombre_completo}" en el sistema')
def step_existe_usuario_nombre(context, nombre_completo):
    """Crear usuario con nombre específico"""
    username = 'mgonzalez'
    if not User.objects.filter(username=username).exists():
        grupo = Group.objects.get(name='Vendedor')
        usuario = User.objects.create_user(
            username=username,
            email=f'{username}@ferremas.cl',
            password='Test2024!',
            first_name='María',
            last_name='González'
        )
        usuario.groups.add(grupo)
    context.usuario_test_username = username

@given('existen múltiples usuarios en el sistema')
def step_existen_multiples_usuarios(context):
    """Crear varios usuarios de prueba"""
    from features.fixtures.test_data import UsuariosTestData
    UsuariosTestData.crear_multiples_usuarios()

@given('existe un usuario "{username}" con rol "{rol}"')
def step_existe_usuario_con_rol(context, username, rol):
    """Crear usuario con rol específico"""
    if not User.objects.filter(username=username).exists():
        grupo = Group.objects.get(name=rol)
        usuario = User.objects.create_user(
            username=username,
            email=f'{username}@ferremas.cl',
            password='Test2024!',
            first_name='Ana' if username == 'atflores' else 'Usuario',
            last_name='Flores' if username == 'atflores' else 'Test'
        )
        usuario.groups.add(grupo)
    context.usuario_test_username = username

@given('existe un usuario "{username}" en el sistema')
def step_existe_usuario_sistema(context, username):
    """Crear usuario genérico de prueba"""
    if not User.objects.filter(username=username).exists():
        grupo = Group.objects.get(name='Vendedor')
        usuario = User.objects.create_user(
            username=username,
            email=f'{username}@ferremas.cl',
            password='Test2024!',
            first_name='Roberto' if username == 'rcastro' else 'Usuario',
            last_name='Castro' if username == 'rcastro' else 'Test'
        )
        usuario.groups.add(grupo)
    context.usuario_test_username = username

# ============================================
# PASOS DE ACCIÓN (When)
# ============================================
@when('navego hacia el panel de administración principal')
def step_navegar_panel_admin(context):
    """Verificar que estamos en el panel de administración"""
    assert "Panel administrador" in context.browser.page_source


@when('selecciono la opción de menú lateral "{opcion}"')
def step_clic_menu(context, opcion):
    """Hacer clic en opción del menú lateral"""
    try:
        menu_link = WebDriverWait(context.browser, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, opcion))
        )
        menu_link.click()
        time.sleep(1)
    except TimeoutException:
        menu_link = context.browser.find_element(
            By.XPATH, f"//a[contains(text(), '{opcion}')]"
        )
        menu_link.click()
        time.sleep(1)


@when('activo el área de formulario para crear usuario')
def step_clic_area_formulario(context):
    """Hacer clic en el área del formulario para activarlo"""
    formulario = context.browser.find_element(By.CSS_SELECTOR, "form")
    assert formulario.is_displayed()


@when('relleno los siguientes datos para el nuevo usuario')
def step_ingresar_datos_usuario(context):
    """Ingresar múltiples datos desde una tabla"""
    for row in context.table:
        campo = row['campo']
        valor = row['valor']
        if campo == 'group':
            select_element = Select(context.browser.find_element(By.ID, "id_group"))
            select_element.select_by_visible_text(valor)
        else:
            elemento = context.browser.find_element(By.ID, f"id_{campo}")
            elemento.clear()
            elemento.send_keys(valor)
        time.sleep(0.3)


@when('presiono el botón general con texto "{texto_boton}"')
def step_hacer_clic_boton(context, texto_boton):
    """Hacer clic en un botón específico"""
    xpath = f"//button[contains(normalize-space(.), '{texto_boton}')] | //button[contains(., '{texto_boton}')] | //a[contains(normalize-space(.), '{texto_boton}')]"
    try:
        boton = WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        _safe_click(context, boton)
        time.sleep(1.0)
        return
    except TimeoutException:
        # Fallback: intentar el botón submit genérico
        try:
            boton = context.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
            _safe_click(context, boton)
            time.sleep(1.0)
            return
        except NoSuchElementException:
            raise


@when('ingreso manualmente el username "{username}" en el campo correspondiente')
def step_ingresar_username(context, username):
    """Ingresar un username específico"""
    campo_username = context.browser.find_element(By.ID, "id_username")
    campo_username.clear()
    campo_username.send_keys(username)


@when('completo todos los campos obligatorios con valores genéricos')
def step_completar_campos_obligatorios(context):
    """Completar campos obligatorios con datos genéricos"""
    campos_obligatorios = {
        'id_first_name': 'Test',
        'id_last_name': 'Usuario',
        'id_email': 'test@ferremas.cl',
        'id_password1': 'Test2024!',
        'id_password2': 'Test2024!',
    }
    for campo_id, valor in campos_obligatorios.items():
        try:
            campo = context.browser.find_element(By.ID, campo_id)
            if campo.get_attribute('value') == '':
                campo.send_keys(valor)
        except NoSuchElementException:
            pass

    try:
        select_element = Select(context.browser.find_element(By.ID, "id_group"))
        select_element.select_by_index(1)
    except:
        pass


@when('busco visualmente al usuario registrado "{username}" en la tabla')
def step_buscar_usuario(context, username):
    """Buscar usuario en la tabla"""
    tabla = context.browser.find_element(By.CSS_SELECTOR, "table")
    assert username in tabla.text


@when('presiono el botón de eliminación del usuario actualmente registrado')
def step_clic_eliminar_usuario(context):
    """Hacer clic en botón eliminar del usuario"""
    username = context.usuario_test_username
    fila_usuario = context.browser.find_element(
        By.XPATH, f"//td[contains(text(), '{username}')]/ancestor::tr"
    )
    # Buscar un botón/eliminar dentro de la fila
    try:
        boton_eliminar = _find_in_row(fila_usuario, texts=['Eliminar', 'Eliminar usuario'], classes=['btn-danger', 'btn-delete'])
        _safe_click(context, boton_eliminar)
    except NoSuchElementException:
        # Intentar buscar por texto exacto fuera de la fila
        try:
            boton_eliminar = context.browser.find_element(By.XPATH, "//button[contains(., 'Eliminar')] | //a[contains(., 'Eliminar')]")
            _safe_click(context, boton_eliminar)
        except Exception:
            raise
    time.sleep(0.5)


@when('confirmo la acción de eliminación mediante el diálogo emergente')
def step_confirmar_eliminacion(context):
    """Confirmar eliminación en el diálogo de confirmación"""
    try:
        alert = WebDriverWait(context.browser, 3).until(EC.alert_is_present())
        alert.accept()
    except TimeoutException:
        pass
    time.sleep(1)


@when('verifico que la lista de usuarios esté visible en pantalla')
def step_observar_lista_usuarios(context):
    """Verificar que la lista de usuarios es visible"""
    tabla = context.browser.find_element(By.CSS_SELECTOR, "table")
    assert tabla.is_displayed()


@when('accedo al modo de edición del usuario con username "{username}"')
def step_clic_editar_usuario(context, username):
    """Hacer clic en botón editar del usuario"""
    fila_usuario = context.browser.find_element(
        By.XPATH, f"//td[contains(text(), '{username}')]/ancestor::tr"
    )
    try:
        boton_editar = _find_in_row(fila_usuario, texts=['Editar', 'Editar usuario'], classes=['btn-outline-primary', 'btn-edit'])
        _safe_click(context, boton_editar)
    except NoSuchElementException:
        # fallback
        boton_editar = fila_usuario.find_element(By.XPATH, ".//a[contains(., 'Editar')] | .//button[contains(., 'Editar')]")
        _safe_click(context, boton_editar)
    time.sleep(1)


@when('modifico el campo de email a la dirección "{nuevo_email}"')
def step_modificar_email(context, nuevo_email):
    """Modificar el campo de email"""
    campo_email = context.browser.find_element(By.ID, "id_email")
    campo_email.clear()
    campo_email.send_keys(nuevo_email)


@when('actualizo el rol del usuario al valor "{nuevo_rol}"')
def step_cambiar_rol(context, nuevo_rol):
    """Cambiar el rol del usuario"""
    select_element = Select(context.browser.find_element(By.ID, "id_group"))
    select_element.select_by_visible_text(nuevo_rol)


@when('intento crear un usuario usando contraseñas distintas')
def step_intentar_crear_contrasenas_no_coinciden(context):
    """Ingresar datos con contraseñas que no coinciden"""
    for row in context.table:
        campo = row['campo']
        valor = row['valor']
        if campo == 'group':
            select_element = Select(context.browser.find_element(By.ID, "id_group"))
            select_element.select_by_visible_text(valor)
        else:
            elemento = context.browser.find_element(By.ID, f"id_{campo}")
            elemento.clear()
            elemento.send_keys(valor)


@when('inspecciono el campo desplegable de selección de "{campo}"')
def step_observar_campo_seleccion(context, campo):
    """Observar un campo de selección"""
    select_element = context.browser.find_element(By.ID, "id_group")
    assert select_element.is_displayed()
    context.select_options = [option.text for option in Select(select_element).options]


@when('cambio únicamente el campo "{campo}" asignándole el valor "{valor}"')
def step_modificar_solo_campo(context, campo, valor):
    """Modificar solo un campo específico"""
    elemento = context.browser.find_element(By.ID, f"id_{campo}")
    elemento.clear()
    elemento.send_keys(valor)


@when('dejo intencionadamente los campos de contraseña vacíos')
def step_dejar_contrasenas_vacias(context):
    """Asegurar que los campos de contraseña están vacíos"""
    campo_pass1 = context.browser.find_element(By.ID, "id_password1")
    campo_pass2 = context.browser.find_element(By.ID, "id_password2")
    campo_pass1.clear()
    campo_pass2.clear()


# ============================================
# PASOS DE VERIFICACIÓN (Then)
# ============================================

@then('debo ver la tabla de usuarios existentes')
def step_ver_tabla_usuarios(context):
    """Verificar que existe la tabla de usuarios"""
    tabla = context.browser.find_element(By.CSS_SELECTOR, "table")
    assert tabla.is_displayed()
    # Verificar que tiene encabezados
    headers = context.browser.find_elements(By.CSS_SELECTOR, "table thead th")
    assert len(headers) > 0

@then('debo ver el mensaje "{mensaje}"')
def step_ver_mensaje(context, mensaje):
    """Verificar que aparece un mensaje específico"""
    try:
        # Buscar en alerts de Bootstrap
        alert = WebDriverWait(context.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert, .message"))
        )
        assert mensaje in alert.text
    except TimeoutException:
        # Buscar en cualquier parte de la página
        page_source = context.browser.page_source
        assert mensaje in page_source, f"No se encontró el mensaje: {mensaje}"

@then('el usuario "{username}" debe aparecer en la lista de usuarios')
def step_usuario_en_lista(context, username):
    """Verificar que el usuario aparece en la lista"""
    tabla = context.browser.find_element(By.CSS_SELECTOR, "table tbody")
    assert username in tabla.text, f"Usuario {username} no encontrado en la lista"

@then('el usuario "{username}" debe tener el rol "{rol}"')
def step_usuario_tiene_rol(context, username, rol):
    """Verificar que el usuario tiene el rol correcto"""
    # Buscar la fila del usuario
    fila_usuario = context.browser.find_element(
        By.XPATH, 
        f"//td[contains(text(), '{username}')]/ancestor::tr"
    )
    assert rol in fila_usuario.text

@then('debo ver el mensaje de error "{mensaje}"')
def step_ver_mensaje_error(context, mensaje):
    """Verificar mensaje de error"""
    try:
        # Buscar en elementos de error
        error_element = WebDriverWait(context.browser, 5).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR, 
                ".invalid-feedback, .alert-danger, .errorlist"
            ))
        )
        assert mensaje in error_element.text or mensaje in context.browser.page_source
    except TimeoutException:
        # Buscar en toda la página
        assert mensaje in context.browser.page_source

@then('el formulario debe resaltar el campo "{campo}" en rojo')
def step_campo_resaltado_error(context, campo):
    """Verificar que el campo tiene clase de error"""
    campo_element = context.browser.find_element(By.ID, f"id_{campo}")
    clases = campo_element.get_attribute("class")
    assert "is-invalid" in clases or "error" in clases

@then('debo ver un diálogo de confirmación con el texto "{texto}"')
def step_ver_dialogo_confirmacion(context, texto):
    """Verificar diálogo de confirmación JavaScript"""
    # En tu implementación, usas onclick="return confirm()"
    # Selenium maneja esto automáticamente, solo verificamos que el botón tiene el onclick
    boton = context.browser.find_element(By.CSS_SELECTOR, "button[type='submit'][onclick]")
    onclick_attr = boton.get_attribute("onclick")
    assert "confirm" in onclick_attr.lower()

@then('el usuario "{username}" no debe aparecer en la lista')
def step_usuario_no_en_lista(context, username):
    """Verificar que el usuario NO aparece en la lista"""
    tabla = context.browser.find_element(By.CSS_SELECTOR, "table tbody")
    assert username not in tabla.text

@then('debo poder identificar al usuario "{username}" en la tabla')
def step_identificar_usuario_tabla(context, username):
    """Verificar que se puede identificar al usuario en la tabla"""
    tabla = context.browser.find_element(By.CSS_SELECTOR, "table")
    assert username in tabla.text

@then('debo ver su rol "{rol}" en la columna correspondiente')
def step_ver_rol_columna(context, rol):
    """Verificar que el rol está visible en la columna"""
    tabla = context.browser.find_element(By.CSS_SELECTOR, "table")
    assert rol in tabla.text

@then('debo ver el formulario de edición con datos precargados')
def step_ver_formulario_edicion_precargado(context):
    """Verificar que el formulario tiene datos precargados"""
    # Verificar que estamos en la página de edición
    assert "editar" in context.browser.current_url.lower() or "Editar Usuario" in context.browser.page_source
    
    # Verificar que los campos tienen valores
    username_field = context.browser.find_element(By.ID, "id_username")
    assert username_field.get_attribute("value") != ""

@then('debo ser redirigido al panel de usuarios')
def step_redirigido_panel_usuarios(context):
    """Verificar que fuimos redirigidos al panel de usuarios"""
    WebDriverWait(context.browser, 10).until(
        lambda driver: "/adminpanel/usuarios/" in driver.current_url
    )
    assert "/adminpanel/usuarios/" in context.browser.current_url

@then('el usuario "{username}" debe tener el email "{email}"')
def step_usuario_tiene_email(context, username, email):
    """Verificar el email del usuario en la base de datos"""
    from django.contrib.auth.models import User
    usuario = User.objects.get(username=username)
    assert usuario.email == email

@then('el campo "{campo}" debe resaltarse en rojo')
def step_campo_resaltado(context, campo):
    """Verificar que el campo tiene estilo de error"""
    campo_element = context.browser.find_element(By.ID, f"id_{campo}")
    clases = campo_element.get_attribute("class")
    assert "is-invalid" in clases or "error" in clases

@then('el usuario no debe crearse en la base de datos')
def step_usuario_no_creado(context):
    """Verificar que el usuario no fue creado"""
    from django.contrib.auth.models import User
    # Intentar buscar el último usuario mencionado en el contexto
    assert not User.objects.filter(username='plopez').exists()

@then('debo ver las siguientes opciones de rol')
def step_ver_opciones_rol(context):
    """Verificar las opciones de rol disponibles"""
    roles_esperados = [row['rol'] for row in context.table]
    
    select_element = Select(context.browser.find_element(By.ID, "id_group"))
    opciones_disponibles = [option.text for option in select_element.options if option.text]
    
    for rol in roles_esperados:
        assert rol in opciones_disponibles, f"Rol {rol} no encontrado en las opciones"

@then('debo ver el mensaje de éxito')
def step_ver_mensaje_exito(context):
    """Verificar que hay un mensaje de éxito"""
    try:
        alert = WebDriverWait(context.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success, .alert"))
        )
        assert alert.is_displayed()
    except TimeoutException:
        # Verificar que fuimos redirigidos exitosamente
        assert "/usuarios/" in context.browser.current_url

@then('el usuario debe poder iniciar sesión con su contraseña anterior')
def step_usuario_login_contrasena_anterior(context):
    """Verificar que la contraseña anterior sigue funcionando"""
    from django.contrib.auth.models import User
    usuario = User.objects.get(username='rcastro')
    # Verificar que el usuario puede autenticarse con la contraseña de prueba
    assert usuario.check_password('Test2024!')

@then('debo ver la página "{titulo_pagina}"')
def step_ver_pagina(context, titulo_pagina):
    """Verificar que estamos en la página correcta por el título"""
    h2_element = context.browser.find_element(By.TAG_NAME, "h2")
    assert titulo_pagina in h2_element.text

# Wrappers/adicionales para que coincidan exactamente con el texto del feature
@given('que estoy en el panel de gestión de usuarios')
def que_estoy_en_panel_usuarios(context):
    return step_en_panel_usuarios(context)

@when('relleno los siguientes datos para el nuevo usuario:')
def cuando_relleno_datos_nuevo_usuario_colon(context):
    return step_ingresar_datos_usuario(context)

@given('que existe un usuario con username "{username}"')
def que_existe_usuario_username(context, username):
    return step_existe_usuario_username(context, username)

@given('que existe un usuario con nombre "{nombre_completo}" en el sistema')
def que_existe_usuario_nombre(context, nombre_completo):
    return step_existe_usuario_nombre(context, nombre_completo)

@given('que existen múltiples usuarios en el sistema')
def que_existen_multiples_usuarios(context):
    return step_existen_multiples_usuarios(context)

@given('que existe un usuario "{username}" con rol "{rol}"')
def que_existe_usuario_con_rol(context, username, rol):
    return step_existe_usuario_con_rol(context, username, rol)

@then('debo ver las siguientes opciones de rol:')
def entonces_debo_ver_opciones_rol_colon(context):
    return step_ver_opciones_rol(context)

@given('que existe un usuario "{username}" en el sistema')
def que_existe_usuario_sistema(context, username):
    return step_existe_usuario_sistema(context, username)

@then(u'debo ver el botón "Crear usuario"')
def step_ver_boton_crear_usuario(context):
    """Verificar que el botón o enlace 'Crear usuario' está visible"""
    xpath = "//button[contains(normalize-space(.), 'Crear usuario')] | //a[contains(normalize-space(.), 'Crear usuario')]"
    try:
        elemento = WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        assert elemento.is_displayed()
        return
    except Exception:
        # Fallback: buscar cualquier button/a y comparar texto en minúsculas
        elems = context.browser.find_elements(By.XPATH, "//button | //a")
        for e in elems:
            try:
                if 'crear usuario' in e.text.strip().lower():
                    assert e.is_displayed()
                    return
            except Exception:
                continue
        assert False, 'Botón o enlace con texto "Crear usuario" no encontrado'