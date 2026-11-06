from typing import Iterable
def filter_voices(voices: list[dict], query: str = "", language: str = "All", gender: str = "All") -> list[dict]:
    query = query.strip().lower()
    result = []
    for voice in voices:
        searchable = " ".join([str(voice.get(key, "")) for key in ("provider", "id", "name", "language", "gender")]).lower()
        if query and query not in searchable:
            continue
        if language != "All" and voice.get("language") != language:
            continue
        if gender != "All" and str(voice.get("gender", "")).lower() != gender.lower():
            continue
        result.append(voice)
    return result
def catalog_facets(voices: Iterable[dict]) -> dict:
    voices = list(voices)
    return {
        "languages": sorted({voice.get("language", "") for voice in voices if voice.get("language")}),
        "genders": sorted({voice.get("gender", "") for voice in voices if voice.get("gender")}),
        "providers": sorted({voice.get("provider", "") for voice in voices if voice.get("provider")}),
    }
def capability_rows(configured_providers: set[str], catalog_counts: dict[str, int]) -> list[dict]:
    capabilities = {
        "Kokoro local": ("Local WAV", "Language, voice, speed", "No credentials"),
        "Azure Speech": ("Cloud MP3", "Voice, language, speed", "API key + region"),
        "Amazon Polly standard": ("Cloud MP3", "Voice, language", "AWS credentials + region"),
        "Amazon Polly neural": ("Cloud MP3", "Voice, language", "AWS credentials + region"),
        "Google Cloud TTS": ("Cloud MP3", "Voice, language", "Service-account JSON"),
    }
    return [{
        "Provider": provider, "Ready": provider in configured_providers,
        "Cached voices": catalog_counts.get(provider, 0), "Output": data[0], "Controls": data[1], "Session requirement": data[2],
    } for provider, data in capabilities.items()]
