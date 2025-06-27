# ClassConnect - API Profiles

## Contenidos
1. Introducción
2. Arquitectura de componentes, Pre-requisitos, CI-CD, Test, Comandos, Despliegue en la nube
3. Test coverage
4. Base de datos
5. Funcionalidades

## 1. Introducción

Microservicio para la gestión de Perfiles en ClassConnect.

Se utilizó por una [arquitectura en capas](https://dzone.com/articles/layered-architecture-is-good).

Permite:
    - Creación de perfiles nuevos.
    - Edición de perfiles.
    - Visualizacion de perfil propio, con todos los datos.
    - Visualización de perfiles de otros, con solo datos publicos.

# 2. Arquitectura de componentes, Pre-requisitos, CI-CD, Test, Comandos, Despliegue en la nube

[Explicados en API Gateway](https://github.com/1c2025-IngSoftware2-g7/api_gateway)

# 3. Test coverage

[Coverage User Service (codecov)](app.codecov.io/github/1c2025-IngSoftware2-g7/service_api_profiles/)

# 4. Base de datos

## PostgreSQL

La base de datos está diseñada para almacenar, consultar y mantener la información crítica relacionada con los usuarios del sistema, incluyendo credenciales, tokens, preferencias y roles.    

# 5. Funcionalidades
1. Edición de perfil:

    Permite a los usuarios modificar los datos de su propio perfil, incluyendo campos como nombre para mostrar, ubicación y otros atributos personales personalizados.

2. Visualización de perfil propio:

    Los usuarios pueden acceder a la información completa y privada de su perfil, con todos los detalles personales almacenados.

3. Visualización de perfil de otros usuarios:

    Permite consultar la información pública de los perfiles de otros usuarios, mostrando solo los datos que no son sensibles o privados.

4. Creación de perfil:

    Proporciona la capacidad para crear un nuevo perfil de usuario con datos iniciales como UUID, nombre, apellido, correo electrónico, rol y otros campos necesarios.

5. Obtención de todos los perfiles:

    Permite recuperar una lista completa con todos los perfiles almacenados en el sistema.

6. Obtención de perfil privado específico
    Permite obtener el perfil completo, con datos privados, de un usuario determinado identificado por su UUID.

7. Obtención de perfil público específico:

    Permite obtener la versión pública del perfil de un usuario determinado identificado por su UUID, ocultando información sensible.

8. Modificación de perfil existente:

    Facilita la actualización de uno o más campos del perfil de un usuario, identificado por su UUID, enviando los datos a modificar.

9. Carga de imagen de perfil:

    Permite subir y asociar una imagen al perfil del usuario, facilitando la personalización visual del perfil.
