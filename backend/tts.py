import edge_tts
import asyncio
import os


async def _generate_edge_voice(text, output_file, language="Tamil", gender="Male"):
    if language == "Tamil":
        voice = "ta-IN-ValluvarNeural" if gender == "Male" else "ta-IN-PallaviNeural"
    else:
        voice = "en-US-GuyNeural" if gender == "Male" else "en-US-JennyNeural"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


def _generate_gtts(text, output_file, language="Tamil"):
    from gtts import gTTS
    lang_code = "ta" if language == "Tamil" else "en"
    tts = gTTS(text=text, lang=lang_code, slow=False)
    tts.save(output_file)


def create_audio(text, output_file, language="Tamil", gender="Male"):
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Try Edge-TTS first (high-fidelity neural voice)
    try:
        asyncio.run(
            _generate_edge_voice(
                text,
                output_file,
                language,
                gender
            )
        )
        if os.path.exists(output_file) and os.path.getsize(output_file) > 100:
            return output_file
    except Exception as e:
        print(f"Notice: Edge-TTS unavailable ({e}). Falling back to gTTS...")

    # Fallback to gTTS (guaranteed availability, zero authentication)
    try:
        _generate_gtts(text, output_file, language)
        return output_file
    except Exception as e:
        raise RuntimeError(f"Audio generation failed across all TTS engines: {e}")


if __name__ == "__main__":

    text = "வணக்கம் நண்பர்களே! நீர் பாதுகாப்பு மிக முக்கியம்."

    output_file = "../output/scene_audio.mp3"

    create_audio(
        text,
        output_file,
        "Tamil",
        "Male"
    )

    print("Audio generated:", output_file)