import asyncio
import edge_tts

text = """
வணக்கம் நண்பர்களே! நான் இந்த கிராமத்தில் ஒரு விவசாயி.
நீர் பாதுகாப்பு மிக முக்கியம்.
மழைநீரை சேமித்து, பாசனத்தை சரியாக பயன்படுத்தி,
நீர் வீணாகாமல் பார்த்துக்கொள்ள வேண்டும்.
"""

async def main():
    voice = "ta-IN-ValluvarNeural"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("../output/test_tamil.mp3")

    print("Tamil audio generated successfully!")

asyncio.run(main())