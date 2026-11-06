from peabox_voice_studio.context import AppContext
import json
import streamlit as st
from peabox_voice_studio.services.catalogs import capability_rows
from peabox_voice_studio.services.files import user_safe_error

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
    st.warning("Credentials are held only in this Streamlit session. They are not saved in projects, exports, manifests, or logs.")
    tabs = st.tabs(["Azure Speech", "Amazon Polly", "Google Cloud TTS"])
    with tabs[0]:
        azure_key = st.text_input("Azure API key", type="password", key="azure_key")
        azure_region = st.text_input("Azure region", profiles.get("Azure Speech", {}).get("region", "centralindia"), key="azure_region")
        if st.button("Use Azure for this session"):
            if azure_key.strip() and azure_region.strip():
                profiles["Azure Speech"] = {"key": azure_key.strip(), "region": azure_region.strip()}; st.success("Azure session profile is ready")
            else: st.error("API key and region are required")
        if st.button("Discover Azure voices", disabled="Azure Speech" not in profiles):
            try:
                from peabox_voice_studio.providers.cloud import discover_azure_voices
                with st.spinner("Discovering Azure voices..."): voice_catalogs["Azure Speech"] = discover_azure_voices(profiles["Azure Speech"])
                st.success(f"Cached {len(voice_catalogs['Azure Speech'])} Azure voices for this session")
            except Exception as exc: st.error("Voice discovery failed: " + user_safe_error(exc))
        if st.button("Clear Azure session profile"):
            profiles.pop("Azure Speech", None); voice_catalogs.pop("Azure Speech", None); st.rerun()
    with tabs[1]:
        aws_access = st.text_input("AWS access key ID", type="password", key="aws_access")
        aws_secret = st.text_input("AWS secret access key", type="password", key="aws_secret")
        aws_token = st.text_input("AWS session token, optional", type="password", key="aws_token")
        aws_region = st.text_input("AWS region", profiles.get("Amazon Polly standard", {}).get("region", "ap-south-1"), key="aws_region")
        if st.button("Use Polly for this session"):
            if aws_access.strip() and aws_secret.strip() and aws_region.strip():
                profile = {"access_key": aws_access.strip(), "secret_key": aws_secret.strip(), "session_token": aws_token.strip(), "region": aws_region.strip()}
                profiles["Amazon Polly standard"] = profile; profiles["Amazon Polly neural"] = profile
                st.success("Polly session profiles are ready")
            else: st.error("Access key, secret key, and region are required")
        polly_engine = st.radio("Polly catalog engine", ["standard", "neural"], horizontal=True)
        if st.button("Discover Polly voices", disabled="Amazon Polly standard" not in profiles):
            try:
                from peabox_voice_studio.providers.cloud import discover_polly_voices
                provider_name = "Amazon Polly neural" if polly_engine == "neural" else "Amazon Polly standard"
                with st.spinner("Discovering Polly voices..."): voice_catalogs[provider_name] = discover_polly_voices(profiles[provider_name], polly_engine)
                st.success(f"Cached {len(voice_catalogs[provider_name])} {provider_name} voices for this session")
            except Exception as exc: st.error("Voice discovery failed: " + user_safe_error(exc))
        if st.button("Clear Polly session profiles"):
            profiles.pop("Amazon Polly standard", None); profiles.pop("Amazon Polly neural", None); voice_catalogs.pop("Amazon Polly standard", None); voice_catalogs.pop("Amazon Polly neural", None); st.rerun()
    with tabs[2]:
        google_file = st.file_uploader("Google service-account JSON", type="json", key="google_profile")
        if st.button("Use Google for this session", disabled=google_file is None):
            try:
                json.loads(google_file.getvalue().decode("utf-8"))
                profiles["Google Cloud TTS"] = {"service_account_json": google_file.getvalue().decode("utf-8")}
                st.success("Google session profile is ready")
            except Exception: st.error("The uploaded file is not valid JSON")
        google_language = st.text_input("Optional Google language filter", value="", key="google_language_filter")
        if st.button("Discover Google voices", disabled="Google Cloud TTS" not in profiles):
            try:
                from peabox_voice_studio.providers.cloud import discover_google_voices
                with st.spinner("Discovering Google voices..."): voice_catalogs["Google Cloud TTS"] = discover_google_voices(profiles["Google Cloud TTS"], google_language)
                st.success(f"Cached {len(voice_catalogs['Google Cloud TTS'])} Google voices for this session")
            except Exception as exc: st.error("Voice discovery failed: " + user_safe_error(exc))
        if st.button("Clear Google session profile"):
            profiles.pop("Google Cloud TTS", None); voice_catalogs.pop("Google Cloud TTS", None); st.rerun()
    counts = {name: len(items) for name, items in voice_catalogs.items()}
    st.subheader("Provider capabilities and readiness")
    st.dataframe(capability_rows(configured_providers(), counts), use_container_width=True, hide_index=True)
    render_sandbox_panel()

# Offline sandbox contract validation is appended to Provider Setup.
def render_sandbox_panel():
 st.divider();st.subheader('Offline provider sandbox');st.caption('Runs deterministic Azure, Polly, and Google request-contract tests without network access or real credentials.')
 if st.button('Run offline provider contract suite'):
  st.session_state['provider_sandbox_results']=run_suite(default_sandboxes())
 results=st.session_state.get('provider_sandbox_results')
 if results:
  st.dataframe([{'Provider':x['provider'],'Passed':x['passed'],'Voices':x['voices'],'Audio fixture bytes':x['audio_bytes'],'Issues':', '.join(x['issues']) or 'None'} for x in results],use_container_width=True,hide_index=True)
  if all(x['passed'] for x in results):st.success('All offline provider contracts passed.')
  else:st.error('One or more provider contracts failed. No live provider call was made.')
 st.info('Sandbox success validates application payloads and normalization only; it does not confirm live credentials, quotas, billing, regional availability, or service status.')
