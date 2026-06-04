def extract_entities(
    summary: str,
    entities: List[dict],
    overall_sentiment: str,
    confidence: float,
    key_topics: List[str]
) -> AnalysisResult:
    """This function exists solely to define the output structure.
    The model will never call it - we just use the tool definition."""
    return AnalysisResult(
        summary=summary,
        entities=[Entity(**e) for e in entities],
        overall_sentiment=overall_sentiment,
        confidence=confidence,
        key_topics=key_topics
    )

response = client.chat.completions.create(
    model="gpt-5.5-2026-04-01",
    messages=[
        {
            "role": "system",
            "content": "Analyze the text and call the extract_entities function with your analysis."
        },
        {
            "role": "user",
            "content": "Apple announced a new partnership with Microsoft..."
        }
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "extract_entities",
            "description": "Extract analysis results from text",
            "parameters": AnalysisResult.model_json_schema()
        }
    }],
    tool_choice={"type": "function", "function": {"name": "extract_entities"}}
)

# Extract the structured data
tool_call = response.choices[0].message.tool_calls[0]
result = AnalysisResult.model_validate_json(
    json.dumps(json.loads(tool_call.function.arguments))
)
