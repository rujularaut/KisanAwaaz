"""
test_tool_calling.py — Test if Sarvam-m supports function/tool calling
Run: python test_tool_calling.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

# pip install openai
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("SARVAM_API_KEY"),
    base_url="https://api.sarvam.ai/v1",
    default_headers={"api-subscription-key": os.getenv("SARVAM_API_KEY")}
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_mandi_price",
            "description": "Fetch mandi price for a crop",
            "parameters": {
                "type": "object",
                "properties": {
                    "commodity": {"type": "string"},
                    "market":    {"type": "string"},
                    "state":     {"type": "string"}
                },
                "required": ["commodity", "market", "state"]
            }
        }
    }
]

print("Testing Sarvam-m tool calling...\n")

try:
    response = client.chat.completions.create(
        model="sarvam-m",
        messages=[
            {"role": "user", "content": "बड़वानी मंडी में टमाटर का भाव क्या है?"}
        ],
        tools=tools,
        tool_choice="auto",
        temperature=0
    )

    message = response.choices[0].message
    print(f"Response: {message}")
    print(f"Tool calls: {message.tool_calls}")

    if message.tool_calls:
        print("\n✅ Sarvam-m SUPPORTS tool calling!")
        tc = message.tool_calls[0]
        print(f"Tool called: {tc.function.name}")
        print(f"Arguments: {tc.function.arguments}")
    else:
        print(f"\n⚠️  No tool call made. Direct response: {message.content}")
        print("Sarvam-m may not support tool calling.")

except Exception as e:
    print(f"❌ Error: {e}")