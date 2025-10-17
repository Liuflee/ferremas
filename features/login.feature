# language: es
Característica: Inicio de sesión
  Para acceder a funciones protegidas
  Como usuario registrado
  Quiero poder iniciar sesión
  Para acceder a mis funciones asignadas

  Antecedentes:
    Dado que el sistema Ferremás está iniciado
    Y estoy en la página de login

  Escenario: Inicio de sesión exitoso
    Cuando inserto usuario "admin_test" y contraseña "admin123" y me autentico
    Entonces debo ver que estoy autenticado como "admin_test"
    Y debo ver el mensaje "Bienvenido admin_test"

  Escenario: Inicio de sesión exitoso con credenciales de cliente
    Cuando inserto usuario "cliente1" y contraseña "Pass123!" y me autentico
    Entonces debo ver que estoy autenticado como "cliente1"
    Y debo ver el mensaje "Bienvenido cliente1"

  Escenario: Inicio de sesión fallido
    Cuando inserto usuario "noexiste" y contraseña "badpass" y me autentico
    Entonces debo ver el mensaje de error "Nombre de usuario o contraseña incorrectos"

  Escenario: Inicio de sesión fallido con usuario vacío
    Cuando inserto usuario "" y contraseña "admin123" y me autentico
    Entonces debo ver el mensaje de error "El campo usuario es obligatorio"

  Escenario: Inicio de sesión fallido con contraseña vacía
    Cuando inserto usuario "admin_test" y contraseña "" y me autentico
    Entonces debo ver el mensaje de error "El campo contraseña es obligatorio"

  Escenario: Validación de campos obligatorios en login
    Cuando inserto usuario "" y contraseña "cualquiera" y me autentico
    Entonces debo ver el mensaje de error "Este campo es obligatorio"
    Cuando inserto usuario "cualquiera" y contraseña "" y me autentico
    Entonces debo ver el mensaje de error "Este campo es obligatorio"

  Escenario: Cerrar sesión
    Dado que estoy autenticado como usuario "admin_test"
    Cuando hago clic en "Cerrar sesión"
    Entonces debo ver la página de login