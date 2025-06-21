# 테스트 코드: test_llama_api.py
from src.llm_interface.llama_api import call_llama

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Give me a very short story about a wizard."}
]

response = call_llama(messages)
print("🧪 Llama 4 응답:\n", response)
