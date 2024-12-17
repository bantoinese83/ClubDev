import asyncio
import base64
import json
import logging
import ssl

import noisereduce as nr
import numpy as np
import sounddevice as sd
from websockets import ConnectionClosedError
from websockets.asyncio.client import connect

from ..core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class GeminiVoice:
    AUDIO_FORMAT = 'int16'
    CHANNELS = 1
    INPUT_RATE = 16000
    OUTPUT_RATE = 24000
    INPUT_BUFFER_SIZE = 1024
    OUTPUT_BUFFER_SIZE = 1024
    NOISE_GATE_THRESHOLD = 500

    def __init__(self):
        self.websocket = None
        self.audio_queue = asyncio.Queue()
        self.api_key = settings.genai_api_key
        self.model_name = "gemini-2.0-flash-exp"
        self.websocket_uri = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={self.api_key}"
        self.output_buffer = bytearray()

    async def start(self):
        """Initialize the WebSocket connection and start audio processing tasks."""
        await self._initialize_websocket()
        logging.info("Connected to Gemini, you can start talking now")
        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(self._capture_audio())
            task_group.create_task(self._stream_audio())
            task_group.create_task(self._play_audio_response())

    async def _initialize_websocket(self):
        """Establish a WebSocket connection."""
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            self.websocket = await connect(
                self.websocket_uri, additional_headers={"Content-Type": "application/json"}, ssl=ssl_context
            )
            await self.websocket.send(json.dumps({"setup": {"model": f"models/{self.model_name}"}}))
            await self.websocket.recv(decode=False)
            logging.info("WebSocket connection established")
        except Exception as error:
            logging.error(f"Failed to connect to WebSocket: {error}")
            raise

    async def _capture_audio(self):
        """Capture audio from the microphone and send it to the WebSocket."""
        loop = asyncio.get_running_loop()

        def callback(indata, frames, time, status):
            if status:
                logging.warning(f"Sounddevice input status: {status}")
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(y=indata.flatten(), sr=self.INPUT_RATE)

            # Send audio data to the WebSocket
            loop.call_soon_threadsafe(asyncio.create_task, self._send_audio_data(reduced_noise.tobytes()))

        try:
            with sd.InputStream(samplerate=self.INPUT_RATE, channels=self.CHANNELS, dtype=self.AUDIO_FORMAT,
                                callback=callback, blocksize=self.INPUT_BUFFER_SIZE) as self.input_stream:
                await asyncio.Future()
        except Exception as e:
            logging.error(f"Error in input capture: {e}")

    async def _send_audio_data(self, audio_data):
        """Send captured audio data to the WebSocket."""
        try:
            await self.websocket.send(
                json.dumps(
                    {
                        "realtime_input": {
                            "media_chunks": [
                                {
                                    "data": base64.b64encode(audio_data).decode(),
                                    "mime_type": "audio/pcm",
                                }
                            ]
                        }
                    }
                )
            )
            logging.debug("Audio data sent")
        except Exception as error:
            logging.error(f"Failed to send audio data: {error}")

    async def _stream_audio(self):
        """Stream audio data from the WebSocket and process server messages."""
        while True:
            try:
                async for message in self.websocket:
                    await self._process_server_message(message)
            except ConnectionClosedError as error:
                logging.error(f"WebSocket connection closed: {error}")
                await self._reconnect_websocket()

    async def _reconnect_websocket(self):
        """Attempt to reconnect to the WebSocket with exponential backoff."""
        backoff_time = 1
        while True:
            try:
                await self._initialize_websocket()
                break
            except Exception as error:
                logging.error(f"Reconnection failed: {error}")
                await asyncio.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, 60)

    async def _process_server_message(self, message):
        """Process messages received from the server."""
        try:
            response = json.loads(message)
            if (
                    "serverContent" in response
                    and "modelTurn" in response["serverContent"]
                    and "parts" in response["serverContent"]["modelTurn"]
                    and response["serverContent"]["modelTurn"]["parts"]
                    and "inlineData" in response["serverContent"]["modelTurn"]["parts"][0]
                    and "data" in response["serverContent"]["modelTurn"]["parts"][0]["inlineData"]
            ):
                audio_data = response["serverContent"]["modelTurn"]["parts"][0]["inlineData"]["data"]
                self.output_buffer.extend(base64.b64decode(audio_data))
                logging.debug("Audio data received and queued")
                if response["serverContent"].get("turnComplete"):
                    logging.info("End of turn")
                    self._clear_audio_queue()
            else:
                logging.debug(f"Skipping message due to missing keys or invalid structure. Content: {message}")
                logging.warning("Skipping message as it does not contain valid audio data.")

        except json.JSONDecodeError as e:
            logging.warning(f"JSONDecodeError encountered: {e}. Message content: {message}")
        except KeyError as error:
            logging.warning(f"KeyError encountered while processing server message: {error}")
            logging.debug(f"Message content: {message}")

    def _clear_audio_queue(self):
        """Clear the audio queue."""
        self.output_buffer = bytearray()
        logging.info("Audio queue cleared")

    async def _play_audio_response(self):
        """Play audio responses from the server."""

        def callback(outdata, frames, time, status):
            if status:
                logging.warning(f"Sounddevice output status: {status}")
            try:
                num_bytes = frames * 2
                if len(self.output_buffer) >= num_bytes:
                    outdata[:] = np.frombuffer(self.output_buffer[:num_bytes], dtype=self.AUDIO_FORMAT).reshape(
                        outdata.shape)
                    del self.output_buffer[:num_bytes]
                else:
                    outdata.fill(0)
            except Exception as e:
                logging.error(f"Error during playback callback: {e}")
                outdata.fill(0)

        try:
            with sd.OutputStream(samplerate=self.OUTPUT_RATE, channels=self.CHANNELS, dtype=self.AUDIO_FORMAT,
                                 callback=callback, blocksize=self.OUTPUT_BUFFER_SIZE) as self.output_stream:
                await asyncio.Future()
        except Exception as e:
            logging.error(f"Error in audio output: {e}")

    async def initialize_websocket(self):
        await self._initialize_websocket()


if __name__ == "__main__":
    client = GeminiVoice()
    asyncio.run(client.start())