from django.db import models

class Empleado(models.Model):
    """
    Modelo para representar a un empleado.
    """
    plataforma = models.CharField(max_length=255)
    pagina = models.CharField(max_length=255)
    usuario = models.CharField(max_length=255, unique=True)
    contraseña = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.usuario} - {self.plataforma}'
