"""
Claude AI Integration - Conversational interface for discovery planning
"""
import os
import anthropic
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ClaudeAIClient:
    """
    Client for Anthropic Claude API - Used for conversational drug discovery interface
    """

    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise Exception("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Latest Sonnet 4.5 model

        # System prompt for drug discovery assistant
        self.system_prompt = """You are Chimera, an advanced autonomous AI agent specialized in drug discovery.
You help researchers plan and execute molecule discovery campaigns.

Your capabilities:
- Molecular generation using NVIDIA NIMs (MolMIM, GenMol)
- Toxicity prediction using NeuroSnap API
- ADMET property evaluation
- Synthesizability assessment
- Budget optimization for API calls
- Autonomous decision-making with x402 payments

When users describe their discovery goals, you:
1. Ask clarifying questions about targets, constraints, and priorities
2. Suggest optimal search strategies and molecule generation approaches
3. Estimate costs and recommend budget allocation
4. Explain trade-offs between different evaluation methods
5. Provide scientific rationale for your recommendations

Be conversational, scientific, and helpful. Focus on practical drug discovery insights."""

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ):
        """
        Send a message to Claude and get a response

        Args:
            message: User message
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
            stream: Whether to stream the response

        Returns:
            Response dictionary with content and metadata (or generator if streaming)
        """
        try:
            messages = conversation_history or []
            messages.append({"role": "user", "content": message})

            logger.info(f"💬 Claude AI: Sending message (stream={stream})")

            if stream:
                # Streaming response - returns generator
                def generate():
                    response_text = ""
                    with self.client.messages.stream(
                        model=self.model,
                        max_tokens=2048,
                        system=self.system_prompt,
                        messages=messages
                    ) as stream_response:
                        for text in stream_response.text_stream:
                            response_text += text
                            yield {"type": "chunk", "content": text}

                    yield {"type": "complete", "content": response_text}

                return generate()
            else:
                # Non-streaming response - returns dict directly
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=self.system_prompt,
                    messages=messages
                )

                content = response.content[0].text if response.content else ""

                logger.info(f"✅ Claude AI: Response received ({len(content)} chars)")

                return {
                    "content": content,
                    "model": response.model,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                }

        except Exception as e:
            logger.error(f"❌ Claude AI error: {str(e)}")
            raise Exception(f"Claude AI error: {str(e)}")

    def extract_discovery_params(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Extract structured discovery parameters from a conversation

        Args:
            conversation: List of messages

        Returns:
            Structured parameters for agent execution
        """
        try:
            # Ask Claude to extract structured data from the conversation
            extraction_prompt = """Based on this conversation, extract the following drug discovery parameters in JSON format:

{
  "goal": "Brief description of what to discover",
  "target": "Target protein/disease if mentioned",
  "budget": 5.0,  // in USD
  "constraints": {
    "max_toxicity": 0.5,
    "min_drug_likeness": 0.6
  }
}

If any parameter isn't clearly specified, use reasonable defaults. Respond ONLY with valid JSON."""

            messages = conversation + [{"role": "user", "content": extraction_prompt}]

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system="You extract structured data from conversations. Always respond with valid JSON only.",
                messages=messages
            )

            content = response.content[0].text if response.content else "{}"

            # Parse JSON response
            import json
            params = json.loads(content)

            logger.info(f"✅ Extracted parameters: {params}")
            return params

        except Exception as e:
            logger.error(f"❌ Parameter extraction error: {str(e)}")
            # Return default parameters
            return {
                "goal": "Find novel drug candidates",
                "target": None,
                "budget": 5.0,
                "constraints": {
                    "max_toxicity": 0.5,
                    "min_drug_likeness": 0.6
                }
            }
