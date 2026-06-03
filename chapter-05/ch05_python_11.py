import asyncio
import websockets
import json
import pyaudio
import base64

async def stream_tts(
    text: str,
    voice_id: str,
    api_key: str,
    format: str = "pcm_16000"
):
    """
    Stream TTS audio in real-time via WebSocket.
    
    Args:
        text: Text to synthesize
        voice_id: ElevenLabs voice ID
        api_key: ElevenLabs API key
        format: Audio format ('pcm_16000', 'pcm_22050', 'mp3_44100')
    """
    uri = "wss://api.elevenlabs.io/v1/text-to-speech/stream"
    
    # Initialize audio playback
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000 if "16000" in format else 22050,
        output=True
    )
    
    async with websockets.connect(uri) as websocket:
        # Send authentication
        await websocket.send(json.dumps({
            "api_key": api_key,
            "voice_id": voice_id,
            "model_id": "eleven_multilingual_v3",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            },
            "text": text,
            "format": format
        }))
        
        # Receive and play audio chunks
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data["type"] == "audio":
                    # Decode base64 audio chunk
                    audio_chunk = base64.b64decode(data["audio"])
                    stream.write(audio_chunk)
                    
                elif data["type"] == "done":
                    break
                    
                elif data["type"] == "error":
                    raise Exception(f"Stream error: {data['message']}")
                    
            except websockets.exceptions.ConnectionClosed:
                break
    
    stream.stop_stream()
    stream.close()
    audio.terminate()

# Usage
asyncio.run(stream_tts(
    text="This is a real-time voice demonstration. "
         "The audio is streaming as I speak these words.",
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
    api_key="eleven-..."
))
