# In `clubdev-backend/app/api/routers/voice_assist_api.py`

from fastapi import APIRouter, HTTPException
import asyncio
import logging

from ...utils.voice_assist_gemini_util import GeminiVoice

voice_assist_router = APIRouter()
logger = logging.getLogger(__name__)

@voice_assist_router.post("/start", tags=["Voice Assist 🗣"], description="Start the voice assistant")
async def start_voice_assist():
    try:
        client = GeminiVoice()
        await client.initialize_websocket()
        asyncio.create_task(client.start())
        logger.info("Voice assistant started successfully")
        return {"message": "Voice assistant started"}
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Connection error")
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(status_code=504, detail="Gateway Timeout: Timeout error")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start voice assistant")