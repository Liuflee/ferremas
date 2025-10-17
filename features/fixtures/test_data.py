
from django.contrib.auth.models import User, Group

class UsuariosTestData:
    """Fixture para crear usuarios de prueba"""
    
    @staticmethod
    def crear_usuario_bodeguero():
        """Crear usuario bodeguero para pruebas"""
        grupo_bodeguero, _ = Group.objects.get_or_create(name='Bodeguero')
        
        if not User.objects.filter(username='mtorres').exists():
            usuario = User.objects.create_user(
                username='mtorres',
                email='mtorres@ferremas.cl',
                password='Bodega2024!',
                first_name='María',
                last_name='Torres'
            )
            usuario.groups.add(grupo_bodeguero)
            return usuario
        return User.objects.get(username='mtorres')
    
    @staticmethod
    def crear_usuario_vendedor():
        """Crear usuario vendedor para pruebas"""
        grupo_vendedor, _ = Group.objects.get_or_create(name='Vendedor')
        
        if not User.objects.filter(username='atflores').exists():
            usuario = User.objects.create_user(
                username='atflores',
                email='atflores@ferremas.cl',
                password='Venta2024!',
                first_name='Ana',
                last_name='Flores'
            )
            usuario.groups.add(grupo_vendedor)
            return usuario
        return User.objects.get(username='atflores')
    
    @staticmethod
    def crear_usuario_contador():
        """Crear usuario contador para pruebas"""
        grupo_contador, _ = Group.objects.get_or_create(name='Contador')
        
        if not User.objects.filter(username='rcastro').exists():
            usuario = User.objects.create_user(
                username='rcastro',
                email='rcastro@ferremas.cl',
                password='Conta2024!',
                first_name='Ricardo',
                last_name='Castro'
            )
            usuario.groups.add(grupo_contador)
            return usuario
        return User.objects.get(username='rcastro')
    
    @staticmethod
    def limpiar_usuarios_test():
        """Eliminar usuarios de prueba después de los tests"""
        usernames_test = ['jperez', 'mgonzalez', 'plopez', 'mtorres', 'atflores', 'rcastro']
        User.objects.filter(username__in=usernames_test).delete()
    
    @staticmethod
    def crear_multiples_usuarios():
        """Crear varios usuarios para pruebas de listado"""
        usuarios_data = [
            {'username': 'user1', 'first_name': 'Usuario', 'last_name': 'Uno', 'grupo': 'Bodeguero'},
            {'username': 'user2', 'first_name': 'Usuario', 'last_name': 'Dos', 'grupo': 'Vendedor'},
            {'username': 'user3', 'first_name': 'Usuario', 'last_name': 'Tres', 'grupo': 'Contador'},
        ]
        
        for data in usuarios_data:
            if not User.objects.filter(username=data['username']).exists():
                grupo = Group.objects.get(name=data['grupo'])
                usuario = User.objects.create_user(
                    username=data['username'],
                    email=f"{data['username']}@ferremas.cl",
                    password='Test2024!',
                    first_name=data['first_name'],
                    last_name=data['last_name']
                )
                usuario.groups.add(grupo)