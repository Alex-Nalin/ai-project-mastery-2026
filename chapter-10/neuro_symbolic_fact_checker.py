# neuro_symbolic_fact_checker.py
import sympy
from pyswip import Prolog
from openai import AsyncOpenAI
from typing import List, Dict, Tuple
import json
import re

class NeuroSymbolicFactChecker:
    def __init__(self, openai_key: str):
        self.llm = AsyncOpenAI(api_key=openai_key)
        self.prolog = Prolog()
        self._initialize_knowledge_base()
        self.symbolic_engine = sympy.Symbol('x')  # Initialize SymPy
    
    def _initialize_knowledge_base(self):
        """Initialize Prolog knowledge base with facts and rules"""
        # Load common knowledge
        self.prolog.consult("""
            % Basic facts
            fact(capital_of, france, paris).
            fact(capital_of, germany, berlin).
            fact(capital_of, japan, tokyo).
            
            % Rules
            is_capital(City, Country) :- fact(capital_of, Country, City).
            
            % Mathematical facts
            fact(pi, 3.14159265359).
            fact(e, 2.71828182846).
            
            % Relationship rules
            located_in(City, Country) :- fact(capital_of, Country, City).
            located_in(City, Country) :- fact(city_in, City, Country).
        """)
    
    async def extract_claims(self, text: str) -> List[Dict]:
        """Use LLM to extract verifiable claims from text"""
        response = await self.llm.chat.completions.create(
            model="gpt-5.5",
            messages=[{
                "role": "system",
                "content": """Extract all verifiable claims from the text. 
For each claim, output JSON with:
- claim: the exact claim
- type: "factual", "mathematical", "logical", "relational"
- confidence: 0-1 estimate of verifiability
- source_text: the exact text supporting the claim"""
            }, {
                "role": "user",
                "content": text
            }]
        )
        
        claims = json.loads(response.choices[0].message.content)
        return claims
    
    def verify_claim_symbolic(self, claim: Dict) -> Dict:
        """Verify a claim using symbolic reasoning"""
        claim_text = claim["claim"]
        claim_type = claim["type"]
        
        if claim_type == "factual":
            return self._verify_factual(claim_text)
        elif claim_type == "mathematical":
            return self._verify_mathematical(claim_text)
        elif claim_type == "logical":
            return self._verify_logical(claim_text)
        elif claim_type == "relational":
            return self._verify_relational(claim_text)
        
        return {"verdict": "unknown", "reason": "Unsupported claim type"}
    
    def _verify_factual(self, claim: str) -> Dict:
        """Verify factual claims using Prolog"""
        # Parse claim into Prolog query
        # e.g., "Paris is the capital of France" -> query(capital_of, france, paris)
        query = self._parse_factual_claim(claim)
        
        if not query:
            return {
                "verdict": "unverifiable",
                "reason": "Could not parse claim into query format",
                "confidence": 0.0
            }
        
        try:
            results = list(self.prolog.query(query))
            if results:
                return {
                    "verdict": "true",
                    "reason": f"Verified: {query} is in knowledge base",
                    "confidence": 0.95,
                    "evidence": str(results)
                }
            else:
                return {
                    "verdict": "unverified",
                    "reason": f"Not found in knowledge base: {query}",
                    "confidence": 0.3
                }
        except Exception as e:
            return {
                "verdict": "error",
                "reason": f"Query error: {str(e)}",
                "confidence": 0.0
            }
    
    def _verify_mathematical(self, claim: str) -> Dict:
        """Verify mathematical claims using SymPy"""
        try:
            # Extract mathematical expression
            expr = self._extract_math_expression(claim)
            
            if not expr:
                return {
                    "verdict": "unverifiable",
                    "reason": "No mathematical expression found",
                    "confidence": 0.0
                }
            
            # Parse and evaluate using SymPy
            parsed = sympy.sympify(expr)
            
            # Check for identity/equality
            if isinstance(parsed, sympy.Equality):
                lhs = parsed.lhs
                rhs = parsed.rhs
                
                # Simplify both sides
                simplified_diff = sympy.simplify(lhs - rhs)
                
                if simplified_diff == 0:
                    return {
                        "verdict": "true",
                        "reason": f"Mathematical identity: {lhs} = {rhs}",
                        "confidence": 1.0,
                        "evidence": str(simplified_diff)
                    }
                else:
                    return {
                        "verdict": "false",
                        "reason": f"Not equal: difference = {simplified_diff}",
                        "confidence": 0.95,
                        "evidence": str(simplified_diff)
                    }
            
            # For numerical verification
            numerical_value = float(parsed.evalf())
            expected_value = self._extract_expected_value(claim)
            
            if expected_value is not None:
                tolerance = 1e-6
                if abs(numerical_value - expected_value) < tolerance:
                    return {
                        "verdict": "true",
                        "reason": f"Numerical match: {numerical_value} ≈ {expected_value}",
                        "confidence": 0.99,
                        "evidence": f"Difference: {abs(numerical_value - expected_value)}"
                    }
                else:
                    return {
                        "verdict": "false",
                        "reason": f"Numerical mismatch: {numerical_value} ≠ {expected_value}",
                        "confidence": 0.99,
                        "evidence": f"Difference: {abs(numerical_value - expected_value)}"
                    }
            
            return {
                "verdict": "true",
                "reason": f"Expression evaluates to {numerical_value}",
                "confidence": 0.9,
                "evidence": str(numerical_value)
            }
            
        except Exception as e:
            return {
                "verdict": "error",
                "reason": f"Mathematical verification error: {str(e)}",
                "confidence": 0.0
            }
    
    def _verify_logical(self, claim: str) -> Dict:
        """Verify logical claims"""
        # Use SymPy for propositional logic
        try:
            # Parse logical statement
            logical_expr = self._parse_logical_expression(claim)
            
            if not logical_expr:
                return {
                    "verdict": "unverifiable",
                    "reason": "Could not parse logical expression",
                    "confidence": 0.0
                }
            
            # Check if tautology
            is_tautology = sympy.simplify(logical_expr) == True
            
            if is_tautology:
                return {
                    "verdict": "true",
                    "reason": "Logical tautology verified",
                    "confidence": 1.0
                }
            
            # Check satisfiability
            variables = list(logical_expr.free_symbols)
            is_satisfiable = self._check_satisfiability(logical_expr, variables)
            
            return {
                "verdict": "satisfiable" if is_satisfiable else "unsatisfiable",
                "reason": f"Logical expression is {'satisfiable' if is_satisfiable else 'unsatisfiable'}",
                "confidence": 0.95
            }
            
        except Exception as e:
            return {
                "verdict": "error",
                "reason": f"Logical verification error: {str(e)}",
                "confidence": 0.0
            }
    
    def _verify_relational(self, claim: str) -> Dict:
        """Verify relational claims using Prolog"""
        try:
            query = self._parse_relational_claim(claim)
            
            if not query:
                return {
                    "verdict": "unverifiable",
                    "reason": "Could not parse relational claim",
                    "confidence": 0.0
                }
            
            results = list(self.prolog.query(query))
            
            if results:
                return {
                    "verdict": "true",
                    "reason": f"Relation verified: {len(results)} matches found",
                    "confidence": 0.9,
                    "evidence": str(results[:5])  # Show first 5 matches
                }
            else:
                return {
                    "verdict": "false",
                    "reason": "No matching relations found",
                    "confidence": 0.7
                }
                
        except Exception as e:
            return {
                "verdict": "error",
                "reason": f"Relational verification error: {str(e)}",
                "confidence": 0.0
            }
    
    async def verify_text(self, text: str) -> Dict:
        """Full pipeline: extract claims, verify each, aggregate results"""
        # Step 1: Extract claims using LLM
        claims = await self.extract_claims(text)
        
        # Step 2: Verify each claim using symbolic engine
        results = []
        for claim in claims:
            verification = self.verify_claim_symbolic(claim)
            results.append({
                "claim": claim["claim"],
                "type": claim["type"],
                "verification": verification
            })
        
        # Step 3: Aggregate results
        verified_true = [r for r in results if r["verification"]["verdict"] == "true"]
        verified_false = [r for r in results if r["verification"]["verdict"] == "false"]
        unverified = [r for r in results if r["verification"]["verdict"] in ["unverified", "unverifiable"]]
        
        return {
            "text": text,
            "total_claims": len(claims),
            "verified_true": len(verified_true),
            "verified_false": len(verified_false),
            "unverified": len(unverified),
            "details": results,
            "overall_verdict": "accurate" if len(verified_false) == 0 else "contains_inaccuracies"
        }

# Usage
checker = NeuroSymbolicFactChecker(openai_key="sk-...")

result = await checker.verify_text("""
The capital of France is Paris. The value of pi is approximately 3.14159. 
If all humans are mortal and Socrates is human, then Socrates is mortal.
The population of Tokyo is 37 million people.
""")

print(f"Overall Verdict: {result['overall_verdict']}")
print(f"Claims Found: {result['total_claims']}")
print(f"Verified True: {result['verified_true']}")
print(f"Verified False: {result['verified_false']}")

for detail in result['details']:
    print(f"  - Claim: {detail['claim']}")
    print(f"    Verdict: {detail['verification']['verdict']}")
    print(f"    Reason: {detail['verification']['reason']}")
