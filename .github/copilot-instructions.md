# Guía para Agentes de IA en el Proyecto Ferremás

## Descripción General del Proyecto
Ferremás es una aplicación web basada en Django que gestiona diferentes roles de usuario (cliente, vendedor, bodeguero, contador) y sus respectivas funcionalidades. El proyecto incluye múltiples aplicaciones Django (`tienda`, `adminpanel`, `bodegueroapp`, `vendedorapp`, `contadorapp`) que encapsulan las responsabilidades específicas de cada rol.

### Componentes Principales
- **Aplicaciones Django**:
  - `tienda`: Funcionalidades generales para clientes.
  - `adminpanel`: Gestión administrativa.
  - `bodegueroapp`: Gestión de inventarios y órdenes de despacho.
  - `vendedorapp`: Gestión de ventas y despacho.
  - `contadorapp`: Resúmenes financieros y reportes.
- **Base de Datos**: Utiliza `db.sqlite3` como base de datos predeterminada.
- **Frontend**: Plantillas HTML con Bootstrap para diseño responsivo.
- **Pruebas**: Pruebas de comportamiento con `behave` y Selenium.

## Flujo de Trabajo
### Configuración Inicial
1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Migrar la base de datos**:
   ```bash
   python manage.py migrate
   ```
3. **Ejecutar el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```

### Pruebas
- Las pruebas de comportamiento están en la carpeta `features/`.
- Ejecutar pruebas con:
  ```bash
  behave
  ```

## Convenciones del Proyecto
- **Autenticación**: Cada rol tiene credenciales predeterminadas (ver `auth_steps.py`).
- **Plantillas**: Cada aplicación tiene su propia carpeta de plantillas bajo `templates/`.
- **Rutas**: Las rutas principales están definidas en `ferremas/urls.py` y delegan a las aplicaciones correspondientes.
- **Estilo de Código**: Sigue las convenciones de PEP 8.

## Puntos de Integración
- **Selenium**: Usado para pruebas de interfaz de usuario.
- **Bootstrap**: Para diseño responsivo.
- **Django REST Framework**: Configurado pero no utilizado ampliamente.

## Archivos Clave
- `ferremas/settings.py`: Configuración global del proyecto.
- `ferremas/urls.py`: Rutas principales.
- `features/`: Pruebas de comportamiento.
- `static/`: Archivos estáticos como CSS e imágenes.

## Ejemplo de Patrón
### Autenticación de Usuarios
El archivo `features/steps/auth_steps.py` contiene pasos reutilizables para autenticar usuarios en pruebas de comportamiento:
```python
def autenticar_usuario(context, username, password, tipo_usuario=""):
    context.browser.get(context.base_url + '/login/')
    user = context.browser.find_element(By.NAME, 'username')
    pwd = context.browser.find_element(By.NAME, 'password')
    user.send_keys(username)
    pwd.send_keys(password)
    btn = context.browser.find_element(By.XPATH, "//button[contains(., 'Entrar')]")
    btn.click()
```

## Notas Adicionales
- **Mensajes de Error**: Verificar mensajes de error en pruebas con clases CSS como `alert-danger`.
- **Roles de Usuario**: Cada rol tiene una página de inicio específica (e.g., `/vendedor/`, `/bodeguero/`).

Para preguntas o problemas, consulta con el equipo de desarrollo.