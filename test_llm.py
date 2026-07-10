"""Quick connectivity check: LangChain ChatOpenAI -> custom Ollama (/v1) over ngrok."""
import os
import json
from langchain_openai import ChatOpenAI

base_url = os.environ.get("LLM_BASE_URL", "https://widen-oops-sandfish.ngrok-free.dev/v1")
model = os.environ.get("LLM_MODEL", "llama3.1:8b")
headers = json.loads(os.environ.get("LLM_EXTRA_HEADERS", '{"ngrok-skip-browser-warning": "true"}'))

llm = ChatOpenAI(
    model=model,
    temperature=0.0,
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
    base_url=base_url,
    default_headers=headers,
)

print(f"Calling {model} at {base_url} ...")
resp = llm.invoke("Reply with exactly one word: pong")
print("Model replied:", repr(resp.content))
