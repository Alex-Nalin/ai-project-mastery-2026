# comparator.py
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from models.base import ModelResponse
from models.openai_wrapper import OpenAIWrapper
from models.anthropic_wrapper import AnthropicWrapper
from models.google_wrapper import GoogleWrapper

@dataclass
class ComparisonResult:
    prompt: str
    responses: List[ModelResponse]
    rankings: List[Dict[str, Any]]

class ModelComparator:
    """Compares responses from multiple AI models and ranks them."""
    
    def __init__(self, openai_key: str, anthropic_key: str, google_key: str):
        self.models = [
            OpenAIWrapper(openai_key, "gpt-5.5"),
            AnthropicWrapper(anthropic_key, "claude-opus-4-8"),
            GoogleWrapper(google_key, "gemini-3.5-pro"),
        ]
        self.console = Console()
    
    async def compare(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful AI assistant.",
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> ComparisonResult:
        """Send the same prompt to all models and collect responses."""
        
        tasks = [
            model.generate(prompt, system_prompt, max_tokens, temperature)
            for model in self.models
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # Filter out errors and rank
        valid_responses = [r for r in responses if r.error is None]
        
        rankings = self._rank_responses(valid_responses, prompt)
        
        return ComparisonResult(
            prompt=prompt,
            responses=responses,
            rankings=rankings
        )
    
    def _rank_responses(
        self, 
        responses: List[ModelResponse],
        original_prompt: str
    ) -> List[Dict[str, Any]]:
        """Rank responses based on quality criteria."""
        
        scored = []
        for response in responses:
            score = 0.0
            
            # Criteria 1: Completeness (does it answer the prompt?)
            score += min(1.0, len(response.content) / 500) * 2.0
            
            # Criteria 2: Structure (has paragraphs, lists, code blocks)
            if '\n\n' in response.content:
                score += 1.0
            if '```' in response.content:
                score += 1.0
            if '- ' in response.content or '1.' in response.content:
                score += 1.0
            
            # Criteria 3: Cost efficiency (cheaper is better)
            cost_score = max(0, 1.0 - (response.cost_usd / 0.1))
            score += cost_score * 1.0
            
            # Criteria 4: Latency (faster is better)
            latency_score = max(0, 1.0 - (response.latency_ms / 10000))
            score += latency_score * 1.0
            
            scored.append({
                'model': response.model_name,
                'provider': response.model_name.split('-')[0].capitalize(),
                'content': response.content,
                'tokens_in': response.input_tokens,
                'tokens_out': response.output_tokens,
                'latency': response.latency_ms,
                'cost': response.cost_usd,
                'score': score
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rank
        for i, item in enumerate(scored, 1):
            item['rank'] = i
        
        return scored
    
    def display_results(self, result: ComparisonResult):
        """Display comparison results in a formatted table."""
        
        self.console.print("\n")
        self.console.print(Panel(
            Text(result.prompt, style="bold cyan"),
            title="[bold]Prompt[/bold]",
            border_style="cyan"
        ))
        
        # Rankings table
        table = Table(title="Model Rankings", show_header=True)
        table.add_column("Rank", style="bold")
        table.add_column("Model", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Cost", style="yellow")
        table.add_column("Latency", style="magenta")
        table.add_column("Tokens", style="blue")
        
        for ranking in result.rankings:
            table.add_row(
                f"#{ranking['rank']}",
                f"{ranking['provider']} - {ranking['model']}",
                f"{ranking['score']:.2f}",
                f"${ranking['cost']:.4f}",
                f"{ranking['latency']:.0f}ms",
                f"{ranking['tokens_in'] + ranking['tokens_out']}"
            )
        
        self.console.print(table)
        
        # Detailed responses
        for ranking in result.rankings:
            self.console.print("\n")
            self.console.print(Panel(
                Text(ranking['content'][:500] + "..."),
                title=f"[bold]Rank #{ranking['rank']}: {ranking['provider']} - {ranking['model']}[/bold]",
                border_style="green" if ranking['rank'] == 1 else "white"
            ))
        
        # Show errors
        errors = [r for r in result.responses if r.error]
        if errors:
            for error in errors:
                self.console.print(f"[red]Error from {error.model_name}: {error.error}[/red]")
