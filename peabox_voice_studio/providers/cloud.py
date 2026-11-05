import html
import json


def azure_list(key: str, region: str):
    import requests
    response = requests.get(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list",
        headers={"Ocp-Apim-Subscription-Key": key}, timeout=30
    )
    response.raise_for_status()
    return response.json()


def azure_generate(text: str, key: str, region: str, voice: str, rate: int, pitch: int) -> bytes:
    import requests
    ssml = (
        "<speak version='1.0' xml:lang='en-US'>"
        f"<voice name='{html.escape(voice, quote=True)}'>"
        f"<prosody rate='{rate}%' pitch='{pitch}%'>{html.escape(text)}</prosody>"
        "</voice></speak>"
    )
    response = requests.post(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml", "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3"},
        data=ssml.encode("utf-8"), timeout=180
    )
    response.raise_for_status()
    return response.content


def aws_client(access_key: str, secret: str, region: str, token: str = ""):
    import boto3
    return boto3.client("polly", region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret, aws_session_token=token or None)


def google_client(raw: str):
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(raw), scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return texttospeech.TextToSpeechClient(credentials=credentials)
