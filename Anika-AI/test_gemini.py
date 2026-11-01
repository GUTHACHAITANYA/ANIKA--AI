import os
import json
import traceback
from dotenv import load_dotenv
import services.ai_service

load_dotenv()

if __name__ == '__main__':
    print('=== GEMINI API CONNECTIVITY TEST ===')
    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    print('GEMINI_API_KEY loaded:', bool(gemini_key and not gemini_key.lower().startswith('your_')))

    try:
        prompt = 'Hello Anika AI test. Please answer with a short, natural text response.'
        response = services.ai_service.call_gemini(prompt, 'You are Anika AI in test mode.', [])
        print('Gemini response:')
        print(json.dumps(response, indent=2))
    except Exception as exc:
        print('Gemini test failed:')
        print(str(exc))
        traceback.print_exc()
