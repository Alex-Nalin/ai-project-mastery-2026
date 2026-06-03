# Bad: Naive character splitting
chunks = [text[i:i+512] for i in range(0, len(text), 512)]

# Good: Semantic chunking
parser = SemanticSplitterNodeParser(
    buffer_size=1024,
    breakpoint_percentile_threshold=95,
)
nodes = parser.get_nodes_from_documents(documents)
