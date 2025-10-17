# language: es
Característica: Gestión de Productos
  Como administrador del sistema
  Quiero gestionar el catálogo de productos
  Para mantener actualizada la oferta de la ferretería

  Antecedentes:
    Dado que el sistema Ferremás está iniciado
    Y estoy en la página de login
    Y me autentico como administrador con usuario "admin_test" y contraseña "admin123"
    Y estoy en el panel de productos

  Escenario: Agregar producto nuevo al catálogo
    Cuando activo el formulario para crear producto
    Y relleno los datos del producto:
      | campo       | valor                        |
      | nombre      | Taladro XYZ                  |
      | descripcion | Taladro profesional 750W     |
      | stock       | 10                           |
      | categoria   | herramientas_electricas      |
      | imagen      | productos/taladro.jpg        |
      | activo      | True                         |
    Y relleno los datos de precio:
      | campo  | valor  |
      | precio | 12990  |
    Y presiono el botón de producto con texto "Crear producto"
    Entonces debo ver el mensaje "Producto creado exitosamente"
    Y debo ver el producto con nombre "Taladro XYZ" en la lista
    Y el precio del producto "Taladro XYZ" debe ser "$12.990"

  Escenario: Modificar producto existente
    Dado que existe un producto con id 1 en el sistema
    Cuando edito el producto con id 1
    Y relleno los datos del producto:
      | campo       | valor                   |
      | nombre      | Taladro Pro             |
      | descripcion | Taladro actualizado     |
    Y relleno los datos de precio:
      | campo  | valor  |
      | precio | 15990  |
    Y presiono el botón de producto con texto "Guardar cambios"
    Entonces debo ver el mensaje "Producto actualizado exitosamente"
    Y debo ver el producto con nombre "Taladro Pro" en la lista
    Y el precio del producto "Taladro Pro" debe ser "$15.990"

  Escenario: Eliminar producto del sistema
    Dado que existe un producto con id 2 en el sistema
    Cuando elimino el producto con id 2
    Y confirmo la eliminación
    Entonces debo ver el mensaje "Producto eliminado correctamente"
    Y no debo ver el producto con id 2 en la lista

  Escenario: Buscar producto por nombre
    Dado que existe un producto con nombre "Martillo Pro" en el sistema
    Cuando busco el producto por nombre "Martillo"
    Entonces debo ver el producto con nombre "Martillo Pro" en la lista

  Escenario: Validación de campos obligatorios en productos
    Cuando activo el formulario para crear producto
    Y relleno los datos del producto:
      | campo      | valor           |
      | precio     | 12990           |
      | stock      | 10              |
    Y presiono el botón de producto con texto "Crear producto"
    Entonces debo ver el mensaje de error "El campo nombre es obligatorio"