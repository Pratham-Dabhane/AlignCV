"""
AlignCV V2 - Mistral 7B Rewrite Engine
Handles resume content rewriting with different styles using Mistral AI.
"""

import logging
import time
from typing import Dict, Optional
import httpx
from ..config import settings

logger = logging.getLogger(__name__)

# Prompt templates for different styles
STYLE_PROMPTS = {
    "Technical": """You are an expert technical resume writer. Rewrite the following resume content to:
- Emphasize technical skills, tools, and technologies
- Use quantifiable metrics (e.g., "improved performance by 40%")
- Highlight problem-solving and technical achievements
- Make it ATS-friendly with relevant keywords
- Keep it concise and impactful

Resume content:
{resume_text}

Return ONLY a JSON object with this exact structure:
{{
  "rewritten_text": "the rewritten resume content here",
  "improvements": ["list of key improvements made"],
  "impact_score": 85
}}""",
    
    "Management": """You are an expert management resume writer. Rewrite the following resume content to:
- Emphasize leadership, team management, and strategic thinking
- Use quantifiable business impact metrics (e.g., "led team of 15", "increased revenue by 25%")
- Highlight stakeholder management and decision-making
- Make it ATS-friendly with relevant keywords
- Keep it concise and impactful

Resume content:
{resume_text}

Return ONLY a JSON object with this exact structure:
{{
  "rewritten_text": "the rewritten resume content here",
  "improvements": ["list of key improvements made"],
  "impact_score": 85
}}""",
    
    "Creative": """You are an expert creative resume writer. Rewrite the following resume content to:
- Emphasize creativity, innovation, and unique contributions
- Use engaging language while maintaining professionalism
- Highlight projects, portfolio work, and creative achievements
- Make it ATS-friendly with relevant keywords
- Keep it concise and impactful

Resume content:
{resume_text}

Return ONLY a JSON object with this exact structure:
{{
  "rewritten_text": "the rewritten resume content here",
  "improvements": ["list of key improvements made"],
  "impact_score": 85
}}"""
}


async def rewrite_resume(
    resume_text: str,
    style: str = "Technical",
    timeout: int = 30
) -> Dict[str, any]:
    """
    Rewrite resume content using Mistral 7B API.
    
    Args:
        resume_text: Original resume content
        style: Rewriting style (Technical, Management, Creative)
        timeout: API request timeout in seconds
        
    Returns:
        Dict with rewritten_text, improvements, impact_score, and metadata
    """
    start_time = time.time()
    
    # Validate style
    if style not in STYLE_PROMPTS:
        logger.warning(f"Invalid style '{style}', defaulting to Technical")
        style = "Technical"
    
    # Check if API key is configured
    if not settings.mistral_api_key or settings.mistral_api_key == "your-mistral-api-key-here":
        logger.warning("Mistral API key not configured, using fallback mode")
        return _fallback_response(resume_text, style)
    
    try:
        # Prepare the prompt
        prompt = STYLE_PROMPTS[style].format(resume_text=resume_text)
        
        # Call Mistral API
        logger.info(f"Calling Mistral API with style: {style}, text length: {len(resume_text)}")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.mistral_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-small-latest",  # Using mistral-small for cost efficiency
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the response
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response from Mistral
            import json
            try:
                # Try to parse as JSON
                parsed_result = json.loads(content)
                rewritten_text = parsed_result.get("rewritten_text", content)
                improvements = parsed_result.get("improvements", [])
                impact_score = parsed_result.get("impact_score", 75)
            except json.JSONDecodeError:
                # If not valid JSON, use content as-is
                logger.warning("Mistral response not valid JSON, using raw content")
                rewritten_text = content
                improvements = ["Content rewritten for better impact"]
                impact_score = 75
            
            latency = time.time() - start_time
            
            logger.info(f"Mistral API success - Latency: {latency:.2f}s, Response length: {len(rewritten_text)}")
            
            return {
                "rewritten_text": rewritten_text,
                "improvements": improvements,
                "impact_score": impact_score,
                "style": style,
                "latency": round(latency, 2),
                "original_length": len(resume_text),
                "rewritten_length": len(rewritten_text),
                "api_status": "success"
            }
            
    except httpx.TimeoutException:
        logger.error(f"Mistral API timeout after {timeout}s")
        return _fallback_response(resume_text, style, error="API timeout")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Mistral API HTTP error: {e.response.status_code} - {e.response.text}")
        return _fallback_response(resume_text, style, error=f"API error: {e.response.status_code}")
        
    except Exception as e:
        logger.error(f"Mistral API unexpected error: {str(e)}")
        return _fallback_response(resume_text, style, error=str(e))


def _fallback_response(resume_text: str, style: str, error: Optional[str] = None) -> Dict[str, any]:
    """
    Fallback response when Mistral API is unavailable or fails.
    Returns original text with a warning.
    """
    warning_msg = "Mistral API unavailable - using original content"
    if error:
        warning_msg = f"Mistral API error ({error}) - using original content"
    
    logger.warning(warning_msg)
    
    return {
        "rewritten_text": resume_text,
        "improvements": [
            "API unavailable - original content preserved",
            f"Requested style: {style}",
            "Please configure MISTRAL_API_KEY for AI rewriting"
        ],
        "impact_score": 0,
        "style": style,
        "latency": 0,
        "original_length": len(resume_text),
        "rewritten_length": len(resume_text),
        "api_status": "fallback",
        "warning": warning_msg
    }


async def extract_keyphrases(text: str, max_phrases: int = 10) -> list:
    """
    Extract key phrases from text using SpaCy.
    Used to enhance resume content with relevant keywords.
    
    Args:
        text: Text to extract phrases from
        max_phrases: Maximum number of phrases to return
        
    Returns:
        List of key phrases
    """
    try:
        from ..nlp.extractor import load_spacy_model
        
        nlp = load_spacy_model()
        doc = nlp(text)
        
        # Extract noun chunks and named entities
        phrases = []
        
        # Add noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:  # Multi-word phrases
                phrases.append(chunk.text.lower().strip())
        
        # Add named entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "SKILL", "GPE"]:
                phrases.append(ent.text.lower().strip())
        
        # Deduplicate and limit
        unique_phrases = list(dict.fromkeys(phrases))[:max_phrases]
        
        logger.info(f"Extracted {len(unique_phrases)} keyphrases from text")
        return unique_phrases
        
    except Exception as e:
        logger.error(f"Keyphrase extraction error: {str(e)}")
        return []
