import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
import os

# Supported languages with language codes
language_codes = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Marathi": "mr",
    "Urdu": "ur"
}

# Custom dictionary for known short phrases
custom_dict = {
    ("hello", "hi"): "नमस्ते",
    ("hello", "te"): "హలో",
    ("hi", "te"): "హాయ్",
    ("how are you", "te"): "మీరు ఎలా ఉన్నారు?",
    ("thank you", "te"): "ధన్యవాదాలు",
    ("i am fine", "te"): "నేను బాగున్నాను",
    ("hello", "ta"): "வணக்கம்",
    ("how are you", "ta"): "நீங்கள் எப்படி இருக்கிறீர்கள்?",
    ("thank you", "ta"): "நன்றி"
}

# Translation function with fallback
def translate_meaningfully(text, src, tgt):
    text = text.strip().lower()
    key = (text, tgt)

    # First check custom dictionary
    if key in custom_dict:
        return custom_dict[key]

    try:
        translated = GoogleTranslator(source=src, target=tgt).translate(text)

        # Try round-trip check to detect transliteration
        if translated.lower() == text:
            round_trip = GoogleTranslator(source=tgt, target=src).translate(translated)
            if round_trip.lower() == text:
                return f"(?) {translated} — may be transliteration"
        return translated
    except Exception as e:
        return f"[Translation Error: {e}]"

# Setup Streamlit
st.set_page_config(page_title="Multi-Language Translator", layout="centered")
st.title("🌐 Multi-Language Voice/Text Translator ")

# Keep user input in session
if "text_input" not in st.session_state:
    st.session_state.text_input = ""

# Input selection
input_mode = st.radio("Choose input type:", ["Text", "Voice"])
source_lang = st.selectbox("Translate from:", list(language_codes.keys()))
target_lang = st.selectbox("Translate to:", list(language_codes.keys()))

# Voice input
if input_mode == "Voice":
    if st.button("🎙️ Record Speech"):
        st.info("🎤 Listening for 5 seconds...")
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio, language=language_codes[source_lang])
                st.session_state.text_input = text
                st.success(f"✅ You said: {text}")
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio.")
        except Exception as e:
            st.error(f"🎙️ Error: {e}")
else:
    st.session_state.text_input = st.text_area(
        "Enter text to translate:", value=st.session_state.text_input
    )

# Translate + Speak
if st.button("🌍 Translate & 🔊 Speak"):
    text = st.session_state.text_input.strip()
    if not text:
        st.warning("⚠️ Please enter or speak something first.")
    else:
        src = language_codes[source_lang]
        tgt = language_codes[target_lang]
        translated = translate_meaningfully(text, src, tgt)

        st.subheader("📝 Translated Output")
        st.success(translated)

        # Speak translated text
        try:
            tts = gTTS(text=translated, lang=tgt)
            tts.save("translated.mp3")
            st.audio("translated.mp3", format="audio/mp3")
        except Exception as e:
            st.error(f"🔊 Text-to-Speech failed: {e}")
