# language: es
Característica: Validación de campos obligatorios

  Escenario: Validación en formulario de producto
    Dado que estoy en el panel de productos
    Cuando activo el formulario para crear producto
    Y relleno los datos del producto:
      | campo  | valor |
      | nombre |       |
    Y presiono el botón de producto con texto "Crear producto"
    Entonces debo ver el mensaje de error "Este campo es obligatorio"