import re
from typing import List, Dict, Optional, Tuple
import json
import httpx

class NeuroSymbolicValidator:
    """Validates LLM outputs against symbolic rules."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Symbolic rules
        self.rules = [
            self._validate_no_hallucinated_numbers,
            self._validate_calculation_consistency,
            self._validate_regulatory_compliance,
            self._validate_date_consistency
        ]
    
    async def generate_and_validate(
        self,
        prompt: str,
        context: Dict,
        model: str = "qwen3.5:32b",
        max_retries: int = 3
    ) -> Tuple[str, List[str]]:
        """Generate response and validate against rules."""
        
        for attempt in range(max_retries):
            # Step 1: Neural generation
            response = await self._generate(prompt, model)
            
            # Step 2: Symbolic validation
            errors = []
            for rule in self.rules:
                rule_errors = await rule(response, context)
                errors.extend(rule_errors)
            
            if not errors:
                return response, []
            
            # Step 3: If validation failed, feed errors back
            if attempt < max_retries - 1:
                correction_prompt = self._build_correction_prompt(
                    prompt, response, errors
                )
                response = await self._generate(correction_prompt, model)
        
        return response, errors  # Return best attempt with warnings
    
    async def _generate(self, prompt: str, model: str) -> str:
        """Generate response from local LLM."""
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "options": {"temperature": 0.3}  # Low temp for accuracy
        }
        response = await self.client.post(
            f"{self.ollama_url}/api/chat",
            json=payload
        )
        return response.json()["message"]["content"]
    
    async def _validate_no_hallucinated_numbers(
        self, response: str, context: Dict
    ) -> List[str]:
        """Check that numerical claims match context."""
        errors = []
        
        # Extract all numbers from response
        numbers = re.findall(r'\$?\d+[.,]?\d*[BMK]?', response)
        
        # Check against known data in context
        for num in numbers:
            clean_num = num.replace('$', '').replace(',', '')
            if clean_num not in str(context.get('known_data', {})):
                # Flag for manual review
                errors.append(f"Unverified numerical claim: {num}")
        
        return errors
    
    async def _validate_calculation_consistency(
        self, response: str, context: Dict
    ) -> List[str]:
        """Verify calculations are internally consistent."""
        errors = []
        
        # Check for percentage calculations
        percentages = re.findall(r'(\d+)%\s+of\s+\$?(\d+[.,]?\d*)', response)
        for pct, amount in percentages:
            expected = float(amount) * float(pct) / 100
            # Look for the result in nearby text
            # This is simplified—real implementation would be more sophisticated
            if f"${expected:,.2f}" not in response:
                errors.append(f"Calculation inconsistency: {pct}% of {amount}")
        
        return errors
    
    async def _validate_regulatory_compliance(
        self, response: str, context: Dict
    ) -> List[str]:
        """Check for regulatory compliance (finance-specific)."""
        errors = []
        
        # Check for required disclaimers
        if "financial advice" in response.lower():
            if "not financial advice" not in response.lower():
                errors.append("Missing required disclaimer")
        
        # Check for prohibited claims
        prohibited_patterns = [
            r'guaranteed\s+returns',
            r'risk-free',
            r'no\s+risk',
        ]
        for pattern in prohibited_patterns:
            if re.search(pattern, response.lower()):
                errors.append(f"Prohibited claim detected: {pattern}")
        
        return errors
    
    async def _validate_date_consistency(
        self, response: str, context: Dict
    ) -> List[str]:
        """Ensure dates and timeframes are consistent."""
        errors = []
        
        # Extract dates
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', response)
        if context.get('reference_date'):
            ref_date = context['reference_date']
            for date in dates:
                if date < ref_date:
                    errors.append(f"Date {date} is before reference date {ref_date}")
        
        return errors
    
    def _build_correction_prompt(
        self, original_prompt: str, response: str, errors: List[str]
    ) -> str:
        """Build a prompt that asks the model to fix errors."""
        correction = f"""
Original request: {original_prompt}

Your previous response had the following issues:
{chr(10).join(f'- {e}' for e in errors)}

Please rewrite your response, correcting all these issues.
Be precise and verify all numbers against the provided data.
"""
        return correction
    
    async def close(self):
        await self.client.aclose()

# Usage example
async def analyze_financial_data():
    validator = NeuroSymbolicValidator()
    
    context = {
        'known_data': {
            'revenue_2025': '2.4B',
            'profit_margin': '18.5%',
            'employees': '12,500'
        },
        'reference_date': '2026-01-01'
    }
    
    prompt = """
    Analyze this company's 2025 performance:
    - Revenue: $2.4B
    - Profit margin: 18.5%
    - Employees: 12,500
    
    Calculate the net profit and provide analysis.
    """
    
    response, errors = await validator.generate_and_validate(prompt, context)
    
    if errors:
        print(f"Warnings ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    print(f"\nResponse:\n{response}")
    await validator.close()
