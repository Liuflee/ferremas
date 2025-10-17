# language: es
Característica: Gestión de Usuarios en Ferremás
  Como administrador del sistema Ferremás
  Quiero gestionar usuarios con diferentes roles
  Para mantener actualizado el sistema de permisos

  Antecedentes:
    Dado que el sistema Ferremás está iniciado
    Y estoy en la página de login
    Y me autentico como administrador con usuario "admin_test" y contraseña "admin123"

  # CP1: Ingreso al mantenedor de usuarios
  Escenario: Acceder al panel de gestión de usuarios
    Cuando navego hacia el panel de administración principal
    Y selecciono la opción de menú lateral "Usuarios"
    Entonces debo ver la página "Gestión de Usuarios"
    Y debo ver el botón "Crear usuario"
    Y debo ver la tabla de usuarios existentes

  # CP2: Registrar usuario en base de datos
  Escenario: Crear un nuevo usuario con rol Bodeguero exitosamente
    Dado que estoy en el panel de gestión de usuarios
    Cuando activo el área de formulario para crear usuario
    Y relleno los siguientes datos para el nuevo usuario:
      | campo      | valor              |
      | username   | jperez             |
      | first_name | Juan               |
      | last_name  | Pérez              |
      | email      | jperez@ferremas.cl |
      | password1  | Bodega2024!        |
      | password2  | Bodega2024!        |
      | group      | Bodeguero          |
    Y presiono el botón general con texto "Crear usuario"
    Y el usuario "jperez" debe aparecer en la lista de usuarios
    Y el usuario "jperez" debe tener el rol "Bodeguero"

  # CP3: No ingresar usuario duplicado a BDD
  Escenario: Intentar crear usuario con nombre de usuario duplicado
    Dado que existe un usuario con username "mtorres"
    Y estoy en el panel de gestión de usuarios
    Cuando activo el área de formulario para crear usuario
    Y ingreso manualmente el username "mtorres" en el campo correspondiente
    Y completo todos los campos obligatorios con valores genéricos
    Y presiono el botón general con texto "Crear usuario"
    Entonces debo ver el mensaje de error "Ya existe un usuario con ese nombre"
    Y el formulario debe resaltar el campo "username" en rojo

  # CP4: Eliminar usuario con confirmación
  Escenario: Eliminar un usuario del sistema con confirmación
    Dado que existe un usuario con nombre "María González" en el sistema
    Y estoy en el panel de gestión de usuarios
    Cuando busco visualmente al usuario registrado "mgonzalez" en la tabla
    Y presiono el botón de eliminación del usuario actualmente registrado
    Entonces debo ver un diálogo de confirmación con el texto "¿Seguro que quieres eliminar este usuario?"
    Cuando confirmo la acción de eliminación mediante el diálogo emergente
    Entonces debo ver el mensaje "Usuario eliminado correctamente"
    Y el usuario "mgonzalez" no debe aparecer en la lista

  # CP5: Actualizar datos de usuario
  Escenario: Modificar información de usuario existente
    Dado que existe un usuario "atflores" con rol "Vendedor"
    Y estoy en el panel de gestión de usuarios
    Cuando accedo al modo de edición del usuario con username "atflores"
    Entonces debo ver el formulario de edición con datos precargados
    Cuando modifico el campo de email a la dirección "ana.flores@ferremas.cl"
    Y actualizo el rol del usuario al valor "Contador"
    Y presiono el botón general con texto "Guardar cambios"
    Entonces debo ver el mensaje "Usuario editado exitosamente con rol: Contador"
    Y debo ser redirigido al panel de usuarios
    Y el usuario "atflores" debe tener el email "ana.flores@ferremas.cl"

  # CP6: Validar contraseñas coincidentes
  Escenario: Validar que las contraseñas coinciden al crear usuario
    Dado que estoy en el panel de gestión de usuarios
    Cuando intento crear un usuario usando contraseñas distintas
      | campo      | valor              |
      | username   | plopez             |
      | first_name | Pedro              |
      | last_name  | López              |
      | email      | plopez@ferremas.cl |
      | password1  | Test2024!          |
      | password2  | Test2025!          |
      | group      | Vendedor           |
    Y presiono el botón general con texto "Crear usuario"
    Entonces debo ver el mensaje de error "Las contraseñas no coinciden"
    Y el campo "password2" debe resaltarse en rojo
    Y el usuario no debe crearse en la base de datos

  # CP7: Verificar roles disponibles
  Escenario: Verificar que los roles del sistema están disponibles
    Dado que estoy en el panel de gestión de usuarios
    Cuando inspecciono el campo desplegable de selección de "Rol"
    Entonces debo ver las siguientes opciones de rol:
      | rol       |
      | Bodeguero |
      | Vendedor  |
      | Contador  |

  # CP8: Editar usuario sin cambiar contraseña
  Escenario: Actualizar datos de usuario sin modificar contraseña
    Dado que existe un usuario "rcastro" en el sistema
    Y estoy en el panel de gestión de usuarios
    Cuando accedo al modo de edición del usuario con username "rcastro"
    Y cambio únicamente el campo "first_name" asignándole el valor "Roberto"
    Y dejo intencionadamente los campos de contraseña vacíos
    Y presiono el botón general con texto "Guardar cambios"
    Entonces debo ver el mensaje de éxito
    Y el usuario debe poder iniciar sesión con su contraseña anterior
