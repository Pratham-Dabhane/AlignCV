"""
AlignCV V2 - LLaMA 3 8B Instruct Rewrite Engine
Handles resume content rewriting with different styles using Meta's LLaMA 3 8B via Groq.
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
    Rewrite resume content using LLaMA 3 8B Instruct via Groq API.
    
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
    if not settings.groq_api_key or settings.groq_api_key == "your-groq-api-key-here":
        logger.warning("Groq API key not configured, using fallback mode")
        return _fallback_response(resume_text, style)
    
    try:
        # Prepare the prompt
        prompt = STYLE_PROMPTS[style].format(resume_text=resume_text)
        
        # Call Groq API with LLaMA 3 8B
        logger.info(f"Calling Groq API (LLaMA 3 8B) with style: {style}, text length: {len(resume_text)}")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",  # LLaMA 3.1 8B Instant (latest)
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
            
            # Parse JSON response from LLaMA
            import json
            try:
                # Try to parse as JSON
                parsed_result = json.loads(content)
                rewritten_text = parsed_result.get("rewritten_text", content)
                improvements = parsed_result.get("improvements", [])
                impact_score = parsed_result.get("impact_score", 75)
            except json.JSONDecodeError:
                # If not valid JSON, use content as-is
                logger.warning("LLaMA response not valid JSON, using raw content")
                rewritten_text = content
                improvements = ["Content rewritten for better impact"]
                impact_score = 75
            
            latency = time.time() - start_time
            
            logger.info(f"Groq API success - Latency: {latency:.2f}s, Response length: {len(rewritten_text)}")
            
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
        logger.error(f"Groq API timeout after {timeout}s")
        return _fallback_response(resume_text, style, error="API timeout")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
        return _fallback_response(resume_text, style, error=f"API error: {e.response.status_code}")
        
    except Exception as e:
        logger.error(f"Groq API unexpected error: {str(e)}")
        return _fallback_response(resume_text, style, error=str(e))


def _fallback_response(resume_text: str, style: str, error: Optional[str] = None) -> Dict[str, any]:
    """
    Fallback response when Groq API is unavailable or fails.
    Returns original text with a warning.
    """
    warning_msg = "Groq API unavailable - using original content"
    if error:
        warning_msg = f"Groq API error ({error}) - using original content"
    
    logger.warning(warning_msg)
    
    return {
        "rewritten_text": resume_text,
        "improvements": [
            "API unavailable - original content preserved",
            f"Requested style: {style}",
            "Please configure GROQ_API_KEY for AI rewriting"
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


async def tailor_resume_to_job(
    resume_text: str,
    job_description: str,
    tailoring_level: str = "moderate",
    timeout: int = 45
) -> Dict[str, any]:
    """
    Tailor a resume to match a specific job description using AI analysis.
    
    This is the key feature that:
    1. Analyzes gaps between resume and job requirements
    2. Suggests specific improvements and keywords to add
    3. Generates a tailored version optimized for the target role
    4. Shows before/after comparison
    
    Args:
        resume_text: Original resume content
        job_description: Target job description to tailor towards
        tailoring_level: How aggressive to tailor (conservative/moderate/aggressive)
        timeout: API request timeout in seconds
        
    Returns:
        Dict with analysis, suggestions, tailored resume, and metadata
    """
    start_time = time.time()
    
    # Validate tailoring level
    valid_levels = ["conservative", "moderate", "aggressive"]
    if tailoring_level not in valid_levels:
        logger.warning(f"Invalid tailoring level '{tailoring_level}', defaulting to moderate")
        tailoring_level = "moderate"
    
    # Check if API key is configured
    if not settings.groq_api_key or settings.groq_api_key == "your-groq-api-key-here":
        logger.warning("Groq API key not configured, using fallback mode")
        return _fallback_tailoring_response(resume_text, job_description, tailoring_level)
    
    try:
        # Create tailored prompt based on level
        prompt = _create_tailoring_prompt(resume_text, job_description, tailoring_level)
        
        logger.info(f"Tailoring resume - Level: {tailoring_level}, Resume: {len(resume_text)} chars, JD: {len(job_description)} chars")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",  # LLaMA 3.1 8B Instant (latest)
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.6,  # Lower temperature for more focused output
                    "max_tokens": 3000  # More tokens for detailed analysis
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the response
            content = result["choices"][0]["message"]["content"]
            finish_reason = result["choices"][0].get("finish_reason", "unknown")
            
            # Log raw LLM response for debugging
            logger.info(f"LLM raw response (first 500 chars): {content[:500]}")
            logger.info(f"LLM response length: {len(content)} chars, finish_reason: {finish_reason}")
            
            # Check if response was truncated
            if finish_reason == "length":
                logger.warning("LLM response was truncated due to max_tokens limit!")
            
            # Parse JSON response - handle various formats
            import json
            import re
            
            parsed_result = None
            
            # Clean the content first - remove any leading/trailing whitespace or markdown
            content_cleaned = content.strip()
            
            # Remove markdown code blocks if present
            if content_cleaned.startswith('```'):
                # Extract content between code blocks
                code_block_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', content_cleaned, re.DOTALL)
                if code_block_match:
                    content_cleaned = code_block_match.group(1).strip()
                    logger.info("Removed markdown code block wrapper")
            
            try:
                # Try direct JSON parse on cleaned content
                parsed_result = json.loads(content_cleaned)
                logger.info("Successfully parsed JSON response")
                
            except json.JSONDecodeError as e:
                # If we get control character error, try using json.JSONDecoder with strict=False
                logger.warning(f"Direct JSON parse failed: {e}")
                
                # Try with strict=False to allow control characters
                try:
                    import json.decoder
                    decoder = json.decoder.JSONDecoder(strict=False)
                    parsed_result = decoder.decode(content_cleaned)
                    logger.info("Successfully parsed JSON with strict=False")
                except Exception as e2:
                    logger.warning(f"Strict=False parsing also failed: {e2}")
                    parsed_result = None
                except Exception as e2:
                    logger.warning(f"Strict=False parsing also failed: {e2}")
                    parsed_result = None
                
                # Strategy 2: Try to find JSON object boundaries and fix control characters
                if parsed_result is None:
                    logger.warning(f"Attempting to fix control characters in JSON")
                    # Find the first { and last }
                    first_brace = content_cleaned.find('{')
                    last_brace = content_cleaned.rfind('}')
                    
                    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                        json_candidate = content_cleaned[first_brace:last_brace + 1]
                        
                        # Try to fix common control character issues
                        # Replace actual newlines in string values with \n
                        # This is a bit hacky but necessary for LLM responses
                        try:
                            # Use ast.literal_eval approach - replace control chars
                            import codecs
                            # Encode to handle special characters, then decode
                            json_fixed = json_candidate.encode('unicode_escape').decode('ascii')
                            # Now decode the escapes properly for JSON
                            json_fixed = codecs.decode(json_fixed, 'unicode_escape')
                            
                            # Try parsing again with strict=False
                            decoder = json.decoder.JSONDecoder(strict=False)
                            parsed_result = decoder.decode(json_candidate)
                            logger.info("Successfully parsed JSON after fixing control characters")
                        except Exception as e3:
                            logger.error(f"Failed to parse after fixing control chars: {e3}")
                            # Log the problematic part
                            logger.error(f"Problematic JSON (first 1000 chars): {json_candidate[:1000]}")
                    else:
                        logger.error("Could not find valid JSON boundaries in response")
            
            # Extract fields from parsed result or use defaults
            if parsed_result:
                tailored_resume = parsed_result.get("tailored_resume", resume_text)
                missing_skills = parsed_result.get("missing_skills", [])
                keyword_suggestions = parsed_result.get("keyword_suggestions", [])
                changes_made = parsed_result.get("changes_made", [])
                match_score = parsed_result.get("match_score", 50)
                priority_improvements = parsed_result.get("priority_improvements", [])
                logger.info(f"Successfully parsed: {len(missing_skills)} missing skills, {len(changes_made)} changes, score: {match_score}")
            else:
                # Fallback if no JSON could be parsed
                logger.warning("Using fallback values - LLM response not valid JSON")
                tailored_resume = content
                missing_skills = []
                keyword_suggestions = []
                changes_made = ["Resume tailored based on job description"]
                match_score = 50
                priority_improvements = []
            
            latency = time.time() - start_time
            
            logger.info(f"Resume tailoring success - Latency: {latency:.2f}s, Match score: {match_score}%")
            
            return {
                "tailored_resume": tailored_resume,
                "original_resume": resume_text,
                "job_description": job_description,
                "match_score": match_score,
                "missing_skills": missing_skills,
                "keyword_suggestions": keyword_suggestions,
                "changes_made": changes_made,
                "priority_improvements": priority_improvements,
                "tailoring_level": tailoring_level,
                "latency": round(latency, 2),
                "original_length": len(resume_text),
                "tailored_length": len(tailored_resume),
                "api_status": "success"
            }
            
    except httpx.TimeoutException:
        logger.error(f"Mistral API timeout after {timeout}s")
        return _fallback_tailoring_response(resume_text, job_description, tailoring_level, error="API timeout")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Mistral API HTTP error: {e.response.status_code} - {e.response.text}")
        return _fallback_tailoring_response(resume_text, job_description, tailoring_level, error=f"API error: {e.response.status_code}")
        
    except Exception as e:
        logger.error(f"Groq API unexpected error: {str(e)}")
        return _fallback_tailoring_response(resume_text, job_description, tailoring_level, error=str(e))


def _create_tailoring_prompt(resume_text: str, job_description: str, tailoring_level: str) -> str:
    """Create a detailed prompt for resume tailoring based on the level."""
    
    level_instructions = {
        "conservative": """Make minimal, subtle changes:
- Only add missing keywords where naturally fitting
- Keep original structure and wording intact
- Focus on highlighting existing relevant experience
- Maintain authenticity and honesty""",
        
        "moderate": """Make balanced, strategic changes:
- Add relevant keywords and phrases from job description
- Reorder sections to emphasize matching experience
- Enhance descriptions to better align with requirements
- Add 2-3 new bullet points if gaps exist""",
        
        "aggressive": """Make comprehensive, bold changes:
- Restructure entire resume to match job requirements
- Add detailed examples for all required skills
- Use exact terminology from job description
- Expand relevant experience, condense less relevant parts
- Add new sections if beneficial (e.g., relevant projects)"""
    }
    
    prompt = f"""You are an expert ATS resume optimization specialist. Your task is to tailor a resume to match a specific job description.

**Tailoring Level**: {tailoring_level.upper()}
{level_instructions[tailoring_level]}

**Original Resume**:
```
{resume_text}
```

**Target Job Description**:
```
{job_description}
```

**Your Task**:
1. Analyze the gap between resume and job requirements
2. Identify missing skills, keywords, and qualifications
3. Generate a tailored resume that addresses these gaps
4. Provide specific changes made and priority improvements

**IMPORTANT**: Return ONLY valid JSON. Do NOT wrap in markdown code blocks. Do NOT add any text before or after the JSON.
All newlines in the "tailored_resume" field MUST be escaped as \\n (not literal newlines).

Return this exact JSON structure (with escaped newlines):
{{
  "tailored_resume": "Name\\nContact Info\\n\\nEDUCATION\\n...",
  "match_score": 85,
  "missing_skills": ["Cloud Architecture", "Agile Methodology", "Full Stack Development"],
  "keyword_suggestions": ["Add 'cloud architecture' to technical skills", "Mention 'Agile methodology' in project descriptions"],
  "changes_made": ["Added FastAPI to skills section", "Emphasized Docker experience in bullet points", "Reordered projects to highlight backend work"],
  "priority_improvements": ["1. Emphasize experience with cloud platforms like AWS and Docker in the skills section. (~20% improvement)", "2. Highlight backend development experience through projects like Complete SDLC Project. (~18% improvement)", "3. Mention Agile methodology in project descriptions to show adaptability and teamwork. (~15% improvement)"]
}}

Be specific, actionable, and honest. Focus on highlighting genuine experience while optimizing presentation.

CRITICAL: Your entire response must be ONLY the JSON object above with properly escaped newlines (\\n). No markdown, no explanations, just pure JSON."""
    
    return prompt


def _fallback_tailoring_response(
    resume_text: str,
    job_description: str,
    tailoring_level: str,
    error: Optional[str] = None
) -> Dict[str, any]:
    """
    Fallback response when Mistral API is unavailable for tailoring.
    Provides basic analysis without AI enhancement.
    """
    warning_msg = "Mistral API unavailable - basic analysis only"
    if error:
        warning_msg = f"Mistral API error ({error}) - basic analysis only"
    
    logger.warning(warning_msg)
    
    # Extract simple keyword matches
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()
    
    # Simple keyword extraction from job description
    jd_words = set(word.strip('.,!?;:') for word in jd_lower.split() if len(word) > 4)
    resume_words = set(word.strip('.,!?;:') for word in resume_lower.split() if len(word) > 4)
    
    missing = list(jd_words - resume_words)[:10]  # Top 10 missing keywords
    
    return {
        "tailored_resume": resume_text,
        "original_resume": resume_text,
        "job_description": job_description,
        "match_score": 0,
        "missing_skills": missing if missing else ["Configure GROQ_API_KEY for detailed analysis"],
        "keyword_suggestions": [
            "API unavailable - manual tailoring recommended",
            f"Requested tailoring level: {tailoring_level}",
            "Please configure GROQ_API_KEY for AI-powered tailoring"
        ],
        "changes_made": ["No changes - API unavailable"],
        "priority_improvements": ["Configure Groq API for AI-powered resume tailoring"],
        "tailoring_level": tailoring_level,
        "latency": 0,
        "original_length": len(resume_text),
        "tailored_length": len(resume_text),
        "api_status": "fallback",
        "warning": warning_msg
    }
