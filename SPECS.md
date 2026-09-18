# auto_short_video
App para crear automáticamente videos cortos (shorts) a partir de un video largo.

## Objetivo
La app debe tomar el video ingresado por el usuario, el título, la potencia del subtitulador, el tiempo de inicio/fin y la cantidad de shorts a crear. Y como resultado entregar cada short al usuario para que pueda ser descargado.

## Alcance
### Puede
1. El usuario puede iniciar sesión.
2. El usuario puede elegir el video base a partir de un link en YT.
3. El usuario puede o no colocar un título que se mostrará en el video.
4. El usuario puede crear varios shorts a partir de un solo video base.
5. El usuario puede descargar los shorts generados.
6. Solo el administrador puede crear y editar usuarios.
7. El usuario puede añadir subtítulos.
8. El usuario puede elegir la capacidad de potencia de la creación automática de subtítulos (entre más potente, el procesamiento lleva más tiempo).

### No puede
1. El usuario no puede guardar datos persistentes en el servidor (los shorts generados deben ser descargados y luego borrados).
2. El usuario no puede personalizar color, posición, fuente, tamaño, etc., de los subtítulos o el título.
3. El usuario no puede incluir o usar sus propios subtítulos.
4. Cualquier cosa no incluida, tomarla como que no está implementada.

## Modelos de Datos
### Entidades persistentes
- Usuario: id (INT), nombre (STRING), username (STRING), password (HASH).

### Datos temporales (en memoria/disco temporal)
- Video base descargado (borrado tras procesar).
- Shorts generados (borrados tras ser descargados por el usuario).

## Reglas de Negocio
1. Solo se puede procesar un video largo a la vez por usuario.
2. Solo se aceptan links de videos de YouTube y que estos sean publicos.
3. Los shorts deben durar mínimo 00:05 y máximo 2:56 minutos.
4. El tiempo de inicio del short debe ser menor que el tiempo de término.
5. Solo se pueden crear hasta 5 shorts a la vez.
6. El título se separa en dos líneas con un máximo de 15 caracteres por línea (máximo 2 líneas = 30 caracteres).

## Casos Límite (Edge Cases)
1. **Link distinto a YouTube**: Si el link para el video largo es distinto a YouTube, rechazar procesamiento con error.
2. **Tiempo inválido**: Si el tiempo de inicio del short es mayor al final, rechazar con error.
3. **Duración inválida**: Si se intenta crear un short menor de 5 segundos o mayor a 2:55 minutos, rechazar con error.
4. **Caracteres del título**: Título con más de 15 letras por línea (2 líneas máximo), rechazar con error.
5. **Fallo de descarga**: Si el video de YouTube es privado o no se puede descargar, mostrar error claro.

## Requisitos No Funcionales
1. **Dependencias**: El servidor debe tener FFmpeg instalado para procesar video.
2. **Memoria/Almacemiento**: Los videos temporales deben borrarse automáticamente al finalizar la descarga o tras un tiempo límite para no llenar el disco del servidor.
3. **Seguridad**: Las contraseñas deben guardarse con hash (bcrypt/argon2)..

## Flujo principal
1. Usuario pega link de YouTube.
2. Sistema valida que sea un link válido.
3. Sistema descarga el video base.
4. Usuario elige tiempos de inicio/fin.
5. Sistema corta el video y genera subtítulos.
6. Sistema guarda el short temporalmente.
7. Usuario descarga el short.
8. Sistema borra el short temporal.