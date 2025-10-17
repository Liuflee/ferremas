# language: es
Característica: Carrito de compras y proceso de pago
  Como cliente registrado
  Quiero agregar productos al carrito y realizar compras
  Para adquirir los productos que necesito

  Antecedentes:
    Dado que el sistema Ferremás está iniciado
    Y estoy en la página de login
    Y me autentico como cliente con usuario "cliente1" y contraseña "Pass123!"
    Y tengo productos en el catálogo

  Escenario: Agregar productos al carrito de compra
    Cuando agrego multiples productos al carrito
      | producto_id |
      | 1           |
      | 2           |
    Y voy a la página del carrito
    Entonces debo ver 2 items en el carrito
    Y debo ver el subtotal correcto

  Escenario: Eliminar producto del carrito
    Dado que tengo un producto en el carrito
    Cuando elimino el producto con id 1 del carrito
    Entonces debo ver 0 items en el carrito
    Y debo ver el mensaje "Carrito actualizado"

  Escenario: Realizar compra completa
    Cuando agrego el producto con id 1 al carrito
    Y procedo al pago desde el carrito
    Y relleno los datos de envío:
      | campo       | valor            |
      | direccion   | Calle 123        |
      | ciudad      | Santiago         |
      | telefono    | +56912345678     |
    Y completo los datos de pago con valores de prueba
    Y finalizo el pago
    Entonces debo ver la página de pago con resultado exitoso
    Y debo ver el mensaje "Tu compra se ha realizado con éxito"

  Escenario: Visualizar historial de compras
    Cuando voy a la página de "mis_pedidos"
    Entonces debo ver la lista de mis pedidos
    Y debo poder ver los detalles del pedido más reciente