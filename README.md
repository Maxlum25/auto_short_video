# auto_short_video
App para crear automáticamente videos cortos (shorts) a partir de un video largo.

## Demo / Capturas
Próximamente.

## Requisitos
- Python 3.13 o superior
- pip
- FFmpeg

## Instalación local
```bash
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Configuración
```bash
cp .env.example .env
```
Edita el archivo `.env` con tus variables de entorno y credenciales.

## Uso
1. Inicia la aplicación.
2. Abre la web en el navegador.
3. Inicia sesión.
4. Elige el video largo al cual se le harán los shorts.
5. Elige las marcas de tiempo de inicio y fin de cada short (se pueden hacer múltiples shorts en base al mismo video largo).
6. Elige para cada short un título que se va a mostrar en el video por arriba (o déjalo vacío).
7. Elige la "potencia" de la IA que va a subtitular el video (entre más potente, más demora).
8. Descarga los shorts ya listos.

## Rutas principales
- `/login`
- `/index`

## API
No aplica en esta versión.

## Tests
Pendiente de implementación.

## Build / Deploy
Pendiente de implementación.

## Errores comunes
- **Archivo `.env` no encontrado**: Ejecuta `cp .env.example .env` para crearlo.
- **FFmpeg no instalado**: Asegúrate de tener FFmpeg instalado en tu sistema operativo.
- **Formato de video no soportado**: Verifica que el video de entrada sea MP4 o un formato compatible.

## Limitaciones
- El color de los subtítulos es fijo (amarillo brillante por defecto).
- El color del título es fijo.

## Roadmap
- Permitir elegir el color de los subtítulos.
- Permitir elegir el color del título.