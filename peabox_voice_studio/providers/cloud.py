import html
import json
from pathlib import Path

from peabox_voice_studio.config import OUTPUTS_DIR
from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename


def generate_azure(text: str, profile: dict, voice: str, speed: float, output_name: str) -> Path:
    import requests
    key = profile["key"]
    region = profile["region"]
    rate = round((speed - 1.0) * 100)
    ssml = (
        "<speak version='1.0' xml:lang='en-US'>"
        f"<voice name='{html.escape(voice, quote=True)}'>"
        f"<prosody rate='{rate}%'>{html.escape(text)}</prosody>"
        "</voice></speak>"
    )
    response = requests.post(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml", "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3"},
        data=ssml.encode("utf-8"), timeout=180,
    )
    response.raise_for_status()
    return atomic_write_bytes(OUTPUTS_DIR / f"{safe_filename(output_name)}.mp3", response.content)


def generate_polly(text: str, profile: dict, voice: str, engine: str, output_name: str) -> Path:
    import boto3
    client = boto3.client(
        "polly", region_name=profile["region"], aws_access_key_id=profile["access_key"],
        aws_secret_access_key=profile["secret_key"], aws_session_token=profile.get("session_token") or None,
    )
    data = client.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId=voice, Engine=engine)["AudioStream"].read()
    return atomic_write_bytes(OUTPUTS_DIR / f"{safe_filename(output_name)}.mp3", data)


def generate_google(text: str, profile: dict, voice: str, language: str, output_name: str) -> Path:
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    info = json.loads(profile["service_account_json"])
    credentials = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    data = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=text),
        voice=texttospeech.VoiceSelectionParams(language_code=language, name=voice),
        audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3),
    ).audio_content
    return atomic_write_bytes(OUTPUTS_DIR / f"{safe_filename(output_name)}.mp3", data)
