import base64
import requests
import os
from fastapi import UploadFile


OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

async def analyze_image(file: UploadFile) -> str:
    """
    Accepts UploadFile from FastAPI → Converts to bytes → Sends to LLM for structured analysis.
    Returns a structured text summary: objects, OCR/text, scene, emotions, business insights, safety.
    """

    if not OPENROUTER_KEY:
        return "❌ Image analysis failed: Missing OPENROUTER_API_KEY."

    
    image_bytes = await file.read()
    b64 = base64.b64encode(image_bytes).decode()

    
    user_message = (
        "You are an expert image analyst. Analyze the given image and return a "
        "clear structured output containing: objects (list), detected text (OCR), "
        "scene summary (one sentence), emotional tone (if people present), "
        "business/marketing insights (2-3 bullets), and safety/NSFW flags. "
        "Return the output in this exact labeled format:\n\n"
        "Objects:\n- ...\n\nDetected Text:\n- ...\n\nScene Summary:\n...\n\nEmotional Tone:\n...\n\nBusiness Insights:\n- ...\n\nSafety:\n- ...\n"
    )

    payload = {
        "model": "gpt-4o-mini", 
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{b64}"}
            ]}
        ],
        "temperature": 0.0,
        "max_tokens": 800
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )

        if resp.status_code != 200:
            return f"❌ Vision API error {resp.status_code}: {resp.text}"

        data = resp.json()

        if "choices" not in data or len(data["choices"]) == 0:
            return "❌ No result from vision model."

       
        return data["choices"][0]["message"].get("content", "❌ No content returned.")

    except Exception as e:
        return f"🔥 Error analyzing image: {str(e)}"




