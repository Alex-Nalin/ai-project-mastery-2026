import google.generativeai as genai

genai.configure(api_key="your-key")
model = genai.GenerativeModel('gemini-3.5-pro-001')

tools = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="get_weather",
                description="Get current weather for a location",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "location": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="City name"
                        ),
                        "units": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            enum=["celsius", "fahrenheit"]
                        )
                    },
                    required=["location"]
                )
            )
        ]
    )
]

response = model.generate_content(
    "What's the weather in Tokyo?",
    tools=tools
)

# Gemini returns function calls in the response
if response.candidates[0].content.parts[0].function_call:
    fc = response.candidates[0].content.parts[0].function_call
    print(f"Function: {fc.name}")
    print(f"Args: {fc.args}")
