# test_generator/generator.py
import ast
import os
from typing import Optional
from pathlib import Path
from anthropic import Anthropic
import black


class TestGenerator:
    """Generates pytest test suites from source code analysis."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])

    def analyze_source(self, file_path: str) -> dict:
        """Parse source code and extract function signatures and docstrings."""
        with open(file_path, "r") as f:
            source = f.read()

        tree = ast.parse(source)

        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": [
                        decorator.id if isinstance(decorator, ast.Name) else str(decorator)
                        for decorator in node.decorator_list
                    ],
                    "docstring": ast.get_docstring(node),
                    "lineno": node.lineno,
                    "returns": self._get_return_type(node),
                }

                # Extract type hints
                for arg in node.args.args:
                    if arg.annotation:
                        func_info[f"type_{arg.arg}"] = self._get_annotation(arg.annotation)

                functions.append(func_info)

            elif isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "methods": [
                        {
                            "name": method.name,
                            "args": [arg.arg for arg in method.args.args],
                            "docstring": ast.get_docstring(method),
                        }
                        for method in node.body
                        if isinstance(method, ast.FunctionDef)
                    ],
                    "docstring": ast.get_docstring(node),
                }
                classes.append(class_info)

        return {
            "file_path": file_path,
            "functions": functions,
            "classes": classes,
            "imports": self._get_imports(tree),
        }

    def _get_annotation(self, node) -> str:
        """Extract type annotation as a string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return f"{self._get_annotation(node.value)}[{self._get_annotation(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return str(node)

    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation."""
        if node.returns:
            return self._get_annotation(node.returns)
        return None

    def _get_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    async def generate_tests(
        self,
        source_file: str,
        output_file: Optional[str] = None,
    ) -> str:
        """Generate pytest tests for a source file."""

        # Analyze the source
        analysis = self.analyze_source(source_file)

        # Read the source code
        with open(source_file, "r") as f:
            source_code = f.read()

        # Generate tests using Claude
        system_prompt = """You are an expert test engineer. Generate comprehensive pytest tests.

For each function or method, generate tests that cover:
1. Happy path (normal input, expected output)
2. Edge cases (empty input, boundary values, None values)
3. Error cases (invalid input, exceptions)
4. Type validation (wrong types, missing required fields)

Rules:
- Use pytest fixtures for common setup
- Use pytest.mark.parametrize for multiple test cases
- Mock external dependencies
- Include descriptive test names and docstrings
- Aim for 90%+ code coverage
- Handle async functions with pytest-asyncio

Generate ONLY the test code, no explanations."""

        user_prompt = f"""Generate pytest tests for the following source code:

File: {analysis['file_path']}

Source Code:
```python
{source_code}
```

Analysis:
- Functions: {[f['name'] for f in analysis['functions']]}
- Classes: {[c['name'] for c in analysis['classes']]}
- Imports: {analysis['imports']}

Generate comprehensive tests following the rules above."""

        response = self.client.messages.create(
            model="claude-opus-4-8-20260415",
            max_tokens=4000,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        test_code = response.content[0].text

        # Format with black
        try:
            test_code = black.format_str(test_code, mode=black.Mode())
        except:
            pass  # If formatting fails, use raw output

        # Write to file
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w") as f:
                f.write(test_code)
            print(f"Tests written to {output_file}")

        return test_code


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="AI-powered test generator")
    parser.add_argument("source", help="Source file to generate tests for")
    parser.add_argument("--output", "-o", help="Output file for tests")
    parser.add_argument("--api-key", help="Anthropic API key")

    args = parser.parse_args()

    generator = TestGenerator(api_key=args.api_key)

    # Generate output filename if not specified
    output_file = args.output
    if not output_file:
        source_path = Path(args.source)
        test_dir = source_path.parent / "tests"
        test_file = test_dir / f"test_{source_path.name}"
        output_file = str(test_file)

    test_code = await generator.generate_tests(
        source_file=args.source,
        output_file=output_file,
    )

    print(f"\nGenerated {len(test_code.splitlines())} lines of tests")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
