# Bot - meetic y telegram
Un bot de automatización que conecta la web de [Meetic](https://www.meetic.es) con Telegram. Permite enviar notificaciones o realizar interacciones automáticas, todo controlado desde un bot seguro y configurable por variables de entorno.

# Stack
```
    - python 3.10+
    - [playwright](https://playwright.dev/python/) (modo async)
    - Telegram Bot API
    - `dotenv`para config sensible
    - Sistema de logging en archivo y consola
    - Asincronia con `asyncio`
```

## Configuracion 
1. clonar el repos
```bash
git clone https://github.com/AntonyCM94/bot-meetic-telegram.git
cd bot-meetic-telegram

2. crea el entorno virtual
```python -m venv .venv
source .venv/bin/activate # en windows: .venv\Scripts\activate

3. instala dependencias
pip install -r requirements.txt

4. Crear el archivo .env con lo siguiente:
    - TELEGRAM_TOKEN=tu_token_aqui
    - TELEGRAM_CHAT_ID=tu_chat_id_aqui

5. ejecutar el bot
python bot.py
```

# Ejemplo de uso
Cuando el bot se ejecuta correctamente, podrás enviar mensajes a tu chat de Telegram con: 
await enviar_mensaje("¡hola desde el bot de meetic!")

El sistema de logs guardará un archivo meetic_bot.log con toda la actividad para depuración

# Estructura
```
meetic-telegram-bot/
├── bot.py
├── .env
├── requirements.txt
├── meetic_bot.log
└── README.md
```

# Seguridad
    - El bot no guarda contraseñas ni datos sensibles en el código
    - Usa .env para almacenar secretos
    - una vez clonado este repos,   no guardar nada público en el archivo .env

# Futuras mejoras

-   Enviar mensajes automáticos a matches desde meetic
-   Sistema de respuestas automáticas según criterios
-   Modo multiusuario con base de datos
-   Panel web para ver estadísticas y logs 

# Autor
Desarrollado pr @Devn-roll con -❤️ y mucho ☕