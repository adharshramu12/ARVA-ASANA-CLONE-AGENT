import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """
You are a UI conversion agent. Convert the following HTML into a clean React component using Tailwind CSS.

Rules:
- Keep container structure
- Replace inline styles with Tailwind classes
- Remove unnecessary wrappers
- Replace long text with placeholders
- Output ONLY React component code, nothing else.

HTML SNIPPET:
"""

def generate_ui(name):
    print(f"[INFO] Loading extracted data for {name}...")
    with open(f"agent/extracted/{name}.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    html = data["html"]

    # Limit size to prevent rate limit (VERY IMPORTANT)
    snippet = html[:8000]  # first 8k chars
    print(f"[INFO] Using {len(snippet)} chars of HTML for generation.")

    print(f"[INFO] Generating React component for {name}...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # ✔ SUPER CHEAP ✔ NO RATE LIMITS
        messages=[
            {"role": "system", "content": "You are an expert React UI generator."},
            {"role": "user", "content": PROMPT + snippet}
        ]
    )

    # Correct extraction syntax
    react_code = response.choices[0].message.content

    os.makedirs("frontend/generated", exist_ok=True)
    output_path = f"frontend/generated/{name.capitalize()}.jsx"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(react_code)

    print(f"[SUCCESS] {name.capitalize()}.jsx generated successfully!")


if __name__ == "__main__":
    generate_ui("home")
    generate_ui("projects")
    generate_ui("tasks")
