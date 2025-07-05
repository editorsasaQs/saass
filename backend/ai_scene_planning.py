import json

import google.generativeai as genai

from .config import GEMINI_API_KEY

# Configure Gemini

genai.configure(api_key=GEMINI_API_KEY)


def get_scene_plan(transcript: str):
    """Generate scene plan from transcript using Gemini Pro."""
    prompt = f"""From this transcript, break into 5–8 scenes. Return:
- start_time, end_time
- subtitle (1-line)
- highlight: true/false
- zoom: true/false
- transition_id (e.g. t1.mp4)

Format:
[
  {{
    \"start\": \"00:00:04\",
    \"end\": \"00:00:12\",
    \"subtitle\": \"Why Your Ads Don't Work\",
    \"highlight\": true,
    \"zoom\": false,
    \"transition_id\": \"t1.mp4\"
  }}
]
TRANSCRIPT:
{transcript}
"""

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    text = response.text.strip()

    # Attempt to parse JSON response
    try:
        plan = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: extract first JSON-like array in the text
        import re
        match = re.search(r"\[.*\]", text, re.S)
        plan = json.loads(match.group()) if match else []

    return plan