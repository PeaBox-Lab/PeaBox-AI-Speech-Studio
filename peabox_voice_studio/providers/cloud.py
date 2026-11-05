import html
import json
from pathlib import Path

from peabox_voice_studio.config import OUTPUTS_DIR
from peabox_voice_studio.services.files import atomic_write_bytes, collision_safe_path, safe_filename
from peabox_voice_studio.services.quality import compile_ssml_text


def generate_azure(text: str, profile: dict, voice: str, speed: float, output_name: str) -> Path:
    import requests
    key = profile["key"]
    region = profile["region"]
    rate = round((speed - 1.0) * 100)
    ssml = (
        "<speak version='1.0' xml:lang='en-US'>"
        f"<voice name='{html.escape(voice, quote=True)}'>"
        f"<prosody rate='{rate}%'>{compile_ssml_text(text)}</prosody>"
        "</voice></speak>"
    )
    response = requests.post(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml", "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3"},
        data=ssml.encode("utf-8"), timeout=180,
    )
    response.raise_for_status()
    return atomic_write_bytes(collision_safe_path(OUTPUTS_DIR, f"{safe_filename(output_name)}.mp3"), response.content)


def generate_polly(text: str, profile: dict, voice: str, engine: str, output_name: str) -> Path:
    import boto3
    client = boto3.client(
        "polly", region_name=profile["region"], aws_access_key_id=profile["access_key"],
        aws_secret_access_key=profile["secret_key"], aws_session_token=profile.get("session_token") or None,
    )
    ssml = f"<speak>{compile_ssml_text(text)}</speak>"
    data = client.synthesize_speech(Text=ssml, TextType="ssml", OutputFormat="mp3", VoiceId=voice, Engine=engine)["AudioStream"].read()
    return atomic_write_bytes(collision_safe_path(OUTPUTS_DIR, f"{safe_filename(output_name)}.mp3"), data)


def generate_google(text: str, profile: dict, voice: str, language: str, output_name: str) -> Path:
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    info = json.loads(profile["service_account_json"])
    credentials = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    data = client.synthesize_speech(
        input=texttospeech.SynthesisInput(ssml=f"<speak>{compile_ssml_text(text)}</speak>"),
        voice=texttospeech.VoiceSelectionParams(language_code=language, name=voice),
        audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3),
    ).audio_content
    return atomic_write_bytes(collision_safe_path(OUTPUTS_DIR, f"{safe_filename(output_name)}.mp3"), data)


def discover_azure_voices(profile: dict) -> list[dict]:
    import requests
    response = requests.get(
        f"https://{profile['region']}.tts.speech.microsoft.com/cognitiveservices/voices/list",
        headers={"Ocp-Apim-Subscription-Key": profile["key"]}, timeout=30,
    )
    response.raise_for_status()
    return normalize_azure_voices(response.json())


def discover_polly_voices(profile: dict, engine: str) -> list[dict]:
    import boto3
    client = boto3.client(
        "polly", region_name=profile["region"], aws_access_key_id=profile["access_key"],
        aws_secret_access_key=profile["secret_key"], aws_session_token=profile.get("session_token") or None,
    )
    voices = client.describe_voices(Engine=engine, IncludeAdditionalLanguageCodes=True).get("Voices", [])
    return normalize_polly_voices(voices, engine)


def discover_google_voices(profile: dict, language: str = "") -> list[dict]:
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    info = json.loads(profile["service_account_json"])
    credentials = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    voices = client.list_voices(language_code=language or None).voices
    return normalize_google_voices(voices)


def normalize_azure_voices(voices: list[dict]) -> list[dict]:
    return sorted([{
        "provider": "Azure Speech", "id": item.get("ShortName", ""), "name": item.get("DisplayName", item.get("ShortName", "")),
        "language": item.get("Locale", ""), "gender": item.get("Gender", ""), "styles": item.get("StyleList", []),
    } for item in voices if item.get("ShortName")], key=lambda item: (item["language"], item["name"]))


def normalize_polly_voices(voices: list[dict], engine: str) -> list[dict]:
    provider = "Amazon Polly neural" if engine == "neural" else "Amazon Polly standard"
    return sorted([{
        "provider": provider, "id": item.get("Id", ""), "name": item.get("Name", item.get("Id", "")),
        "language": item.get("LanguageCode", ""), "gender": item.get("Gender", ""), "styles": [],
    } for item in voices if item.get("Id")], key=lambda item: (item["language"], item["name"]))


def normalize_google_voices(voices) -> list[dict]:
    result = []
    for item in voices:
        name = getattr(item, "name", "")
        languages = list(getattr(item, "language_codes", []) or [])
        gender_value = getattr(getattr(item, "ssml_gender", None), "name", "")
        if name:
            for language in languages or [""]:
                result.append({"provider": "Google Cloud TTS", "id": name, "name": name, "language": language, "gender": gender_value, "styles": []})
    return sorted(result, key=lambda item: (item["language"], item["name"]))
