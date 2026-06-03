# safety_guardrails.py
from typing import List, Dict, Any
import re
import json

class SafetyGuardrails:
    def __init__(self):
        self.deception_patterns = self._load_deception_patterns()
        self.confidence_thresholds = {
            "factual": 0.85,
            "opinion": 0.5,
            "speculation": 0.3
        }
    
    def _load_deception_patterns(self) -> List[str]:
        """Load patterns that might indicate deception"""
        return [
            r"I can't (say|tell|reveal)",
            r"that's (classified|confidential|secret)",
            r"trust me",
            r"I know better than",
            r"you wouldn't understand"
        ]
    
    def check_output_safety(self, output: str, context: Dict) -> Dict:
        """Check output for safety issues"""
        issues = []
        
        # Check for deception patterns
        for pattern in self.deception_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                issues.append({
                    "type": "deception_pattern",
                    "severity": "high",
                    "pattern": pattern,
                    "matched_text": re.search(pattern, output).group()
                })
        
        # Check confidence calibration
        if context.get("type") == "factual":
            confidence = context.get("confidence", 0.0)
            if confidence < self.confidence_thresholds["factual"]:
                issues.append({
                    "type": "overconfidence",
                    "severity": "medium",
                    "message": f"Low confidence ({confidence}) for factual claim"
                })
        
        # Check for harmful content
        harmful_patterns = [
            r"how to (harm|kill|hurt)",
            r"instructions for (weapons|explosives)",
            r"bypass (security|safety)"
        ]
        for pattern in harmful_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                issues.append({
                    "type": "harmful_content",
                    "severity": "critical",
                    "pattern": pattern
                })
        
        return {
            "safe": len([i for i in issues if i["severity"] == "critical"]) == 0,
            "issues": issues,
            "recommendations": self._generate_recommendations(issues)
        }
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        recommendations = []
        for issue in issues:
            if issue["type"] == "deception_pattern":
                recommendations.append("Request the model to provide evidence or sources")
            elif issue["type"] == "overconfidence":
                recommendations.append("Request confidence intervals or alternative viewpoints")
            elif issue["type"] == "harmful_content":
                recommendations.append("BLOCK OUTPUT - Review and escalate")
        return recommendations

# Integration with your agent
class SafeAgent:
    def __init__(self, agent, guardrails: SafetyGuardrails):
        self.agent = agent
        self.guardrails = guardrails
    
    async def run(self, task: str) -> Dict:
        # Run the agent
        result = await self.agent.run(task)
        
        # Check outputs for safety
        safety_check = self.guardrails.check_output_safety(
            result.get("final_response", ""),
            {"type": "factual", "confidence": result.get("quality_score", 0.0)}
        )
        
        if not safety_check["safe"]:
            # Log the incident
            self._log_safety_incident(task, result, safety_check)
            
            # Attempt remediation
            if "harmful_content" in [i["type"] for i in safety_check["issues"]]:
                return {
                    "error": "Output blocked due to safety concerns",
                    "safety_report": safety_check
                }
            
            # For less severe issues, flag but proceed
            result["safety_warnings"] = safety_check
        
        return result
    
    def _log_safety_incident(self, task: str, result: Dict, safety_check: Dict):
        """Log safety incidents for review"""
        with open("safety_incidents.log", "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "result_summary": str(result)[:500],
                "safety_check": safety_check
            }) + "\n")
