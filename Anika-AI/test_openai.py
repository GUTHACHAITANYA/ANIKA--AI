import os
import json
import traceback
from dotenv import load_dotenv
from services.ai_service import call_openai

load_dotenv()

if __name__ == '__main__':
    print('=== OPENAI API CONNECTIVITY TEST ===')
    openai_key = os.getenv('OPENAI_API_KEY', '').strip()
    print('OPENAI_API_KEY loaded:', bool(openai_key and not openai_key.lower().startswith('your_')))

    try:
        prompt = 'Hello Anika AI test. Please answer with a short, natural text response.'
        response = call_openai(prompt, 'You are Anika AI in test mode.', [])
        print('OpenAI response:')
        print(json.dumps(response, indent=2))
    except Exception as exc:
        print('OpenAI test failed:')
        print(str(exc))
        traceback.print_exc()
