from django.contrib.auth.models import Group

def es_vendedor(user):
    return user.is_authenticated and user.groups.filter(name='Vendedor').exists()

def es_bodeguero(user):
    return user.is_authenticated and user.groups.filter(name='Bodeguero').exists()

def es_contador(user):
    return user.is_authenticated and user.groups.filter(name='Contador').exists()