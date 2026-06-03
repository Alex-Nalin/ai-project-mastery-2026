import requests

class ElevenLabsVoiceAgent:
    """Create and manage ElevenLabs Voice Agents."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def create_agent(
        self,
        name: str,
        voice_id: str,
        system_prompt: str,
        first_message: str = "Hello! How can I help you today?",
        temperature: float = 0.3
    ) -> str:
        """
        Create an autonomous voice agent.
        
        Args:
            name: Agent name
            voice_id: Voice to use
            system_prompt: Instructions for agent behavior
            first_message: Initial greeting
            temperature: Response creativity (0.0–1.0)
        
        Returns:
            Agent ID
        """
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": name,
            "voice_id": voice_id,
            "system_prompt": system_prompt,
            "first_message": first_message,
            "temperature": temperature,
            "max_duration_seconds": 600,
            "enable_transcriber": True,
            "enable_agent": True
        }
        
        response = requests.post(
            f"{self.base_url}/agents",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["agent_id"]
    
    def start_conversation(self, agent_id: str, phone_number: str = None) -> str:
        """
        Start a conversation with the agent.
        
        Args:
            agent_id: Agent identifier
            phone_number: Optional phone number for PSTN calls
        
        Returns:
            Conversation ID
        """
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {"agent_id": agent_id}
        if phone_number:
            payload["phone_number"] = phone_number
        
        response = requests.post(
            f"{self.base_url}/conversations",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["conversation_id"]

# Example: Customer support agent
agent = ElevenLabsVoiceAgent(api_key="eleven-...")

agent_id = agent.create_agent(
    name="Support Bot",
    voice_id="21m00Tcm4TlvDq8ikWAM",
    system_prompt=(
        "You are a helpful customer support agent for TechCorp. "
        "You handle questions about our SaaS platform, "
        "troubleshoot common issues, and escalate complex problems. "
        "Be friendly, professional, and concise. "
        "If you cannot resolve an issue, offer to transfer to a human agent."
    ),
    first_message="Welcome to TechCorp support! "
                  "I'm your AI assistant. How can I help you today?"
)
