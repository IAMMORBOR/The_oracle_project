from openai import OpenAI
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

r = client.chat.completions.create(
    model    = "gpt-4o",
    max_tokens = 20,
    messages = [{"role": "user", "content": "Say hello"}]
)

print("API works:", r.choices[0].message.content)