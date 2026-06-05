# daily-brief

Sistema minimo para generar cada dia un brief con 5 noticias relevantes desde fuentes RSS aprobadas, curarlas con OpenAI y enviarlas por Telegram.

## Requisitos

- Python 3.11+
- Una API key de OpenAI
- Un bot de Telegram y el chat id de destino

## Instalacion local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env`:

```env
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789
```

Configura las fuentes en `config/sources.yaml`, tus intereses en `config/interests.yaml` y el prompt principal en `config/prompt.md`.

## Ejecucion

```bash
python -m src.main
```

Por defecto usa `data/daily_brief.sqlite3` para recordar articulos ya enviados y evitar repeticiones.

## Despliegue en servidor Linux

1. Copia el proyecto al servidor.
2. Crea el entorno virtual e instala dependencias:

```bash
cd /opt/daily-brief
python3.11 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

3. Rellena `.env` con tus credenciales.
4. Prueba una ejecucion manual:

```bash
. /opt/daily-brief/.venv/bin/activate
cd /opt/daily-brief
python -m src.main
```

5. Programa cron, por ejemplo todos los dias a las 06:00:

```cron
0 6 * * * cd /opt/daily-brief && . .venv/bin/activate && python -m src.main >> logs/cron.log 2>&1
```

## Estructura

```text
config/
  sources.yaml      # RSS aprobados
  interests.yaml    # perfil, intereses y reglas
  prompt.md         # instrucciones principales para el LLM
src/
  main.py           # orquestador
  fetch_sources.py  # lectura RSS
  dedupe.py         # deduplicacion por URL y titulo similar
  database.py       # SQLite
  llm.py            # seleccion y redaccion con OpenAI
  telegram_sender.py
  models.py
  config_loader.py
data/
logs/
```

## Notas

- Si una fuente falla, el sistema continua con las demas.
- Si no hay suficientes candidatos nuevos, el brief puede contener menos de 5 noticias.
- El mensaje se envia en Markdown compatible con Telegram.
