Pruebas de comportamiento (behave) para Ferremás

Requisitos:
- Python con dependencias: `pip install -r requirements.txt`
- Chrome y chromedriver en PATH (o usar otro webdriver y ajustar `features/environment.py`)

Ejecutar todas las pruebas:
  behave

Ejecutar un feature en particular:
  behave features/auth.feature

Variables de entorno útiles:
- FERREMAS_BASE_URL: URL base de la aplicación (por defecto http://localhost:8000)
- HEADLESS=0 para ver el navegador en vez de headless
