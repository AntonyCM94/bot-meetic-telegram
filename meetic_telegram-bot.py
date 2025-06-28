from playwright.async_api import async_playwright  # Cambio: async_api
from telegram.ext import Application
import asyncio
import time
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configurar logging SIN emojis para Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meetic_bot.log', encoding='utf-8'),  # UTF-8 para archivo
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# configuraciones
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MEETIC_URL = "https://www.meetic.es/"

# Debug de variables de entorno (SIN emojis)
logger.info("=== INICIANDO BOT MEETIC ===")
logger.info(f"TELEGRAM_TOKEN configurado: {'SI' if TELEGRAM_TOKEN else 'NO'}")
logger.info(f"TELEGRAM_CHAT_ID configurado: {'SI' if TELEGRAM_CHAT_ID else 'NO'}")
logger.info(f"TELEGRAM_CHAT_ID valor: {TELEGRAM_CHAT_ID}")  # Debug del valor real
logger.info(f"URL objetivo: {MEETIC_URL}")

async def enviar_mensaje(texto):
    """Envía un mensaje al chat de Telegram."""
    try:
        logger.info(f"[Telegram] Preparando envio de mensaje...")
        logger.debug(f"[Telegram] Mensaje: {texto[:100]}...")
        
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        await app.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)
        
        logger.info(f"[Telegram] Mensaje enviado correctamente")
        
    except Exception as e:
        logger.error(f"[Telegram] Error enviando mensaje: {e}")
        raise

async def scrapear_meetic():
    """Scrapea la página de Meetic y envía un mensaje con el número de usuarios."""
    logger.info("=== INICIANDO SCRAPING DE MEETIC ===")
    
    try:
        async with async_playwright() as p:  # Cambio: async_playwright
            logger.info("[Playwright] Iniciando navegador...")
            browser = await p.chromium.launch(headless=False)  # Cambio: await
            page = await browser.new_page()  # Cambio: await
            
            logger.info(f"[Playwright] Navegando a: {MEETIC_URL}")
            await page.goto(MEETIC_URL)  # Cambio: await
            logger.info("[Playwright] Pagina cargada")

            # Debug: Capturar screenshot inicial
            await page.screenshot(path=f"debug_meetic_{int(time.time())}.png")  # Cambio: await
            logger.info("[Debug] Screenshot guardado")

            # Pausa manual para login
            logger.warning("[MANUAL] Esperando login manual...")
            input("[INFO] Inicia sesion en Meetic y presiona Enter para continuar...")
            logger.info("[MANUAL] Continuando tras login manual")

            # Debug: Verificar título de página
            titulo = await page.title()  # Cambio: await
            logger.info(f"[Debug] Titulo de pagina: {titulo}")

            # Buscar perfiles
            logger.info("[Scraping] Buscando perfiles...")
            perfiles = await page.query_selector_all("article")  # Cambio: await
            logger.info(f"[Scraping] Encontrados {len(perfiles)} elementos <article>")

            # Debug: Listar todos los selectores disponibles
            if len(perfiles) == 0:
                logger.warning("[Debug] No se encontraron <article>. Probando otros selectores...")
                
                # Probar selectores alternativos
                selectores_alternativos = [
                    ".profile-card",
                    ".user-card", 
                    "[data-testid*='profile']",
                    ".card",
                    ".member"
                ]
                
                for selector in selectores_alternativos:
                    elementos = await page.query_selector_all(selector)  # Cambio: await
                    logger.info(f"[Debug] Selector '{selector}': {len(elementos)} elementos")

            if not perfiles: 
                mensaje_error = f"ERROR: No se encontraron perfiles en Meetic.\nTitulo: {titulo}\nURL: {page.url}"
                logger.warning("[Scraping] No se encontraron perfiles")
                await enviar_mensaje(mensaje_error)
            else: 
                logger.info(f"[Scraping] Procesando {min(len(perfiles), 3)} perfiles...")
                
                for i, perfil in enumerate(perfiles[:3]):
                    logger.info(f"[Scraping] Procesando perfil {i+1}/3")
                    
                    try:
                        # Debug del perfil
                        perfil_html = await perfil.inner_html()  # Cambio: await
                        logger.debug(f"[Debug] HTML del perfil {i+1}: {perfil_html[:200]}...")
                        
                        # Buscar nombre
                        nombre_elem = await perfil.query_selector("h2")  # Cambio: await
                        nombre = await nombre_elem.inner_text() if nombre_elem else "Desconocido"  # Cambio: await
                        logger.info(f"[Scraping] Nombre encontrado: {nombre}")
                        
                        # Buscar descripción
                        descripcion = await perfil.inner_text()  # Cambio: await
                        logger.info(f"[Scraping] Descripcion: {len(descripcion)} caracteres")
                        
                        mensaje = f"NUEVO perfil detectado:\nNombre: {nombre}\nDescripcion: {descripcion[:150]}..."
                        await enviar_mensaje(mensaje)
                        
                        # Pausa entre mensajes
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"[Scraping] Error procesando perfil {i+1}: {e}")

            logger.info("[Playwright] Cerrando navegador...")
            await browser.close()  # Cambio: await
            logger.info("[Playwright] Navegador cerrado")

    except Exception as e:
        logger.error(f"[Scraping] Error general: {e}")
        raise

if __name__ == "__main__":
    async def main():
        ciclo = 1
        while True:
            try:
                logger.info(f"=== CICLO {ciclo} - {datetime.now()} ===")
                await scrapear_meetic()
                logger.info(f"Ciclo {ciclo} completado exitosamente")
                
            except Exception as e:
                logger.error(f"Error en ciclo {ciclo}: {e}")
                try:
                    await enviar_mensaje(f"ERROR en ciclo {ciclo}: {str(e)[:200]}...")
                except:
                    logger.error("No se pudo enviar mensaje de error")
            
            logger.info("Esperando 1 hora para el proximo ciclo...")
            await asyncio.sleep(3600)
            ciclo += 1
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.critical(f"Error critico: {e}")