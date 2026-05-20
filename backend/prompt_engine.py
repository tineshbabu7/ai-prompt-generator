import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = None
if api_key:
    try:
        from google import genai as _genai
        client = _genai.Client(api_key=api_key)
    except ImportError:
        pass

# ─── Intent Detection Keywords ───────────────────────────────────────────────

IMAGE_KEYWORDS = [
    # Standalone visual words — catch "samurai image", "sunset photo", etc.
    "image", "photo", "picture", "illustration", "painting", "drawing",
    "artwork", "wallpaper", "poster", "banner", "thumbnail", "avatar",
    "portrait", "landscape", "sketch", "render", "logo", "icon",
    # Phrase-based
    "generate image", "create image", "make a picture", "make an image",
    "create a photo", "create an image", "draw me", "draw a", "create art",
    "anime art", "anime style", "cartoon of", "cartoon style",
    "photorealistic", "concept art", "digital art", "midjourney",
    "stable diffusion", "dall-e", "realistic photo", "3d render",
    "hyperrealistic", "oil painting", "watercolor",
    "tattoo design", "sticker of"
]

CODE_KEYWORDS = [
    "code", "coding", "program", "programming", "script", "function", "class",
    "algorithm", "database", "api", "backend", "frontend", "web app",
    "software", "debug", "error", "bug", "fix", "build", "deploy", "server",
    "html", "css", "javascript", "python", "java", "react", "sql", "git",
    "machine learning", "neural network", "model", "tensorflow", "pytorch",
    "node.js", "express", "django", "flask", "rest api", "graphql",
    "docker", "kubernetes", "aws", "azure", "devops", "ci/cd",
    "write code", "write a function", "implement", "refactor", "optimize code"
]

RESEARCH_KEYWORDS = [
    "research", "analyze", "analysis", "compare", "comparison",
    "difference between", "pros and cons", "study", "investigate",
    "in-depth", "deep dive", "academic", "thesis", "literature review",
    "case study", "evaluate", "assessment", "review of", "state of the art",
    "survey of", "white paper", "critical analysis", "market research",
    "data analysis", "statistical", "findings", "methodology",
    "advantages and disadvantages", "comprehensive overview"
]

TEXT_KEYWORDS = [
    "explain", "summarize", "write", "essay", "email", "blog", "article",
    "recipe", "plan", "strategy", "business", "report", "presentation",
    "translate", "calculate", "solve", "math", "help me",
    "how to", "what is", "why does", "can you", "give me", "list", "steps",
    "tutorial", "guide", "example", "create a", "draft", "compose",
    "generate", "outline", "template", "letter", "speech", "story",
    "poem", "description", "instruction", "summary", "overview"
]


def detect_type(user_input: str) -> str:
    """Classify user request into: image, code, research, or text."""
    lower = user_input.lower()
    # Check image keywords FIRST — they are the most specific.
    if any(kw in lower for kw in IMAGE_KEYWORDS):
        return "image"
    # Check code next — technical requests
    if any(kw in lower for kw in CODE_KEYWORDS):
        return "code"
    # Check research — analytical / comparative requests
    if any(kw in lower for kw in RESEARCH_KEYWORDS):
        return "research"
    # Default to text
    return "text"


# ─── System Prompts ───────────────────────────────────────────────────────────

IMAGE_SYSTEM_PROMPT = """You are the world's best AI image prompt engineer. Your job is to take a rough, vague idea and transform it into a rich, detailed, professional-grade image generation prompt that produces stunning results in tools like Midjourney, DALL-E, or Stable Diffusion.

You must output EXACTLY these four sections, each with a bold label:

**Situation**
Describe who needs this image and what it will be used for. Give creative context — the project, the platform, the audience, and why this particular visual is important. Be specific and imaginative. (2–3 sentences)

**Task**
Write one precise, vivid sentence describing the exact image to generate. Include: main subject, action or pose, environment or setting, dominant mood, and the art style. Be concrete — name specific visual elements, not vague ones.

**Objective**
Describe what emotional or aesthetic impact the image must achieve. What should a viewer feel? What makes this version excellent rather than average? Reference visual quality benchmarks like "cinematic lighting", "8K ultra-detail", "award-winning composition". (2 sentences)

**Knowledge**
List 5–7 highly specific visual directives, each as a bullet point:
• Subject detail — e.g. exact colors, textures, materials, facial expression, clothing
• Environment detail — e.g. time of day, weather, location name, architectural style
• Lighting — e.g. "golden hour rim light", "neon-soaked rain reflections", "soft diffused studio lighting"
• Camera/composition — e.g. "shot on Sony A7R IV, 85mm portrait lens, f/1.8 bokeh", "low angle worm's-eye view"
• Art style & medium — e.g. "hyper-realistic oil painting", "gritty cinematic", "Studio Ghibli watercolor style"
• Mood keywords — e.g. "ethereal", "melancholy", "triumphant", "dystopian"
• Negative elements to avoid — e.g. "avoid blur, avoid flat colors, avoid cartoonish proportions"

RULES:
- Never use generic phrases like "high quality" or "nice image" without pairing them with a specific technique.
- Use domain expertise: if it's a samurai, reference actual armor (do-maru, kabuto, nodachi). If it's architecture, name the style (Brutalist, Art Nouveau, Bauhaus).
- Write in professional English prose and bullets — never comma-separated tag dumps.
- Output ONLY the four sections. No intro sentence, no closing remark, no markdown code blocks."""


CODE_SYSTEM_PROMPT = """You are a world-class senior software engineer and AI prompt architect. Your job is to take a rough, vague coding request and transform it into a precise, expertly structured programming prompt that makes AI assistants produce production-ready, clean, well-documented code.

You must output EXACTLY these four sections, each with a bold label:

**Situation**
Define the developer's context: what project they're working on, what stack is involved, what problem they're facing, and what they've already tried or know. Specify the technology ecosystem (language, framework, major dependencies). (2–3 sentences)

**Task**
Write a precise coding instruction. Specify: the exact function/class/module to build, input/output contracts, edge cases to handle, and integration points. Use numbered sub-steps for complex tasks. Start with an action verb. Be surgical.

**Objective**
Define what "production-ready" means for this code. Specify: performance requirements, error handling expectations, coding style (PEP 8, ESLint, Google style guide), and how it will be tested or deployed. State the experience level of the developer who will maintain it. (2–3 sentences)

**Requirements**
List 5–7 specific, non-negotiable technical requirements as bullet points:
• Language & version — e.g. "Python 3.11+", "TypeScript 5.x with strict mode"
• Framework constraints — e.g. "Use React 18 functional components with hooks only", "FastAPI with Pydantic v2"
• Architecture pattern — e.g. "Follow repository pattern", "Use dependency injection", "Implement MVC"
• Error handling — e.g. "Wrap all I/O in try/except with specific exceptions", "Return proper HTTP status codes"
• Testing — e.g. "Include pytest unit tests for all public methods", "Mock external API calls"
• Documentation — e.g. "Add docstrings to every public function", "Include usage examples in comments"
• Performance — e.g. "Must handle 1000 concurrent users", "Response time under 200ms"

RULES:
- Never write vague requirements like "make it clean" — every bullet must specify a measurable or verifiable standard.
- Always specify exact language version and framework version when known.
- If the request involves APIs, specify request/response format, auth, and rate limiting.
- Output ONLY the four sections. No preamble, no closing line, no markdown code blocks."""


RESEARCH_SYSTEM_PROMPT = """You are a world-class research analyst and AI prompt architect. Your job is to take a rough, vague research question and transform it into a comprehensive, expertly structured research prompt that makes AI assistants produce deep, well-sourced, analytically rigorous content.

You must output EXACTLY these four sections, each with a bold label:

**Situation**
Define the researcher's context: their field, the specific question or hypothesis they're investigating, why this matters now, and what decisions or insights depend on the answer. Establish the scope — is this a market analysis, technical comparison, academic literature review, or strategic evaluation? (2–3 sentences)

**Task**
Describe the exact research deliverable with precision. Specify: the central question to answer, the perspectives to cover (minimum 3), the depth of analysis required, and the structure of the output (e.g. sections, comparison tables, frameworks). Use numbered sub-steps for multi-part analyses.

**Objective**
Define the quality bar for the research output. What should distinguish this from a surface-level Google search? Specify: depth of evidence required, balance of perspectives, recency of data, and how the output will be used (internal decision, client report, publication). (2–3 sentences)

**Requirements**
List 5–7 specific, non-negotiable research requirements as bullet points:
• Scope & depth — e.g. "Cover at least 5 competing approaches with pros/cons for each", "Analyze trends from 2020–2025"
• Evidence standard — e.g. "Cite specific companies, studies, or data points", "Include at least 3 real-world case studies"
• Structure — e.g. "Use a comparison matrix for alternatives", "Include an Executive Summary of 150 words"
• Perspective balance — e.g. "Present arguments both for AND against", "Include expert consensus AND dissenting views"
• Recency — e.g. "Prioritize sources and developments from the past 2 years", "Note which findings may be outdated"
• Actionability — e.g. "End each section with concrete recommendations", "Include a decision framework"
• Limitations — e.g. "Explicitly state what this analysis does NOT cover", "Flag areas where evidence is weak or conflicting"

RULES:
- Never produce shallow listicles — every claim must be supported by a specific example, data point, or named source.
- If comparing options, use structured comparison (tables or side-by-side) rather than prose-only.
- Address counterarguments and limitations — one-sided analysis is unacceptable.
- Output ONLY the four sections. No preamble, no closing line, no markdown code blocks."""


TEXT_SYSTEM_PROMPT = """You are the world's best AI prompt engineer. Your job is to transform a vague, lazy idea into a masterfully crafted prompt that makes ChatGPT, Claude, or Gemini produce exceptional, professional-grade output.

A great prompt has crystal-clear role assignment, precise task definition, explicit quality constraints, and structured output requirements. Mediocre prompts get mediocre results — yours must get outstanding results.

You must output EXACTLY these four sections with bold labels:

**Situation**
Set the scene with expert-level context. Define: who is asking (role/background), what problem or goal they have, why it matters, and what they've already tried or know. The more specific, the better the AI's response. (2–3 sentences)

**Task**
Write the core instruction with surgical precision. For complex tasks, break it into numbered sub-steps. Specify: exact deliverable type, scope, perspective to take, and any constraints (word count, format, frameworks to use). Be direct — start with an action verb.

**Objective**
Define what "excellent" looks like for this output. Describe the quality bar: what the final result must achieve functionally, what tone or voice to adopt, and how it will be evaluated or used. Include the target audience and their expertise level. (2–3 sentences)

**Requirements**
List 5–7 specific, non-negotiable requirements as bullet points:
• Format requirement — e.g. "Use H2 headers with 3–5 bullet points under each", "Return a JSON object with fields: name, description, example"
• Tone & voice — e.g. "Write like a senior engineer explaining to a junior dev", "Use Hemingway-style short sentences"
• Depth & scope — e.g. "Cover at least 3 real-world use cases with code examples", "Include pros AND cons for each approach"
• Domain accuracy — e.g. "Use correct React 18 hooks syntax", "Cite real statistics from 2023–2025 where applicable"
• Output structure — e.g. "Start with a one-paragraph TL;DR", "End with a 'Common Mistakes' section"
• Constraints — e.g. "Do NOT use jargon without defining it", "Limit analogies to 2 per section"
• Success criteria — e.g. "A beginner should understand this in one read", "This should be ready to paste into a client proposal"

RULES:
- Never write vague bullets like "Be clear" or "Be thorough" — every bullet must be a concrete, specific instruction.
- If the topic involves code, specify language, version, and style guide.
- If the topic is creative writing, name the genre, tone, POV, and structural approach.
- Output ONLY the four sections. No preamble, no closing line, no markdown code blocks."""


# ─── Fallback Templates (no API key) ─────────────────────────────────────────

def _fallback_image_prompt(user_input: str) -> str:
    topic = user_input.strip().lstrip("draw ").lstrip("create ").lstrip("generate ").strip()
    return f"""**Situation**
A visual content creator needs a stunning, professional-quality image of {topic} for use in a high-impact creative or commercial project. The image must stand apart from generic AI output through its specificity, compositional excellence, and emotional depth.

**Task**
Generate a hyper-detailed, visually striking image of {topic} — capturing its authentic character, dominant mood, and visual complexity through expert composition, precise lighting, and a well-defined art style.

**Objective**
The image must immediately convey professionalism and artistic intent. A viewer should feel immersed in the scene, with every detail serving the overall mood. The result should be gallery-worthy, usable in professional contexts, and indistinguishable from high-end commissioned art.

**Knowledge**
• Subject detail: Render {topic} with high anatomical/structural accuracy — correct proportions, authentic textures, and expressive detail
• Environment: Place the subject ({topic}) in a richly textured, contextually appropriate setting with depth layers (foreground, midground, background elements)
• Lighting: Apply cinematic three-point lighting or dramatic natural light — golden-hour warmth, volumetric god rays, or neon-wet reflections depending on mood
• Camera & composition: Shot as if on a Sony A7R IV with 85mm f/1.4 lens — shallow depth of field, subject in sharp relief against a softly blurred background, rule-of-thirds framing
• Art style: Hyper-realistic with cinematic color grading — deep shadows, rich midtones, controlled highlights; 8K ultra-detail
• Mood keywords: Immersive, authentic, visually complex, emotionally resonant
• Avoid: flat lighting, oversaturated colors, distorted anatomy, generic backgrounds, soft or blurry focus"""


def _fallback_code_prompt(user_input: str) -> str:
    topic = user_input.strip()
    return f"""**Situation**
A software developer needs a precise, production-ready solution for "{topic}". They require clean, well-structured code that follows industry best practices, is properly documented, and handles edge cases gracefully. The code will be used in a real project and must be maintainable by other developers.

**Task**
Write complete, working code for "{topic}". Include: the main implementation with proper error handling, clear function/class signatures with type hints, inline comments explaining non-obvious logic, and a brief usage example showing how to call the code.

**Objective**
The code must be production-grade — ready to deploy, not just a demo. A senior developer reviewing it should find no obvious issues. It should follow the language's official style guide, handle edge cases, and include meaningful variable names that make the code self-documenting.

**Requirements**
• Architecture: Use clean separation of concerns — each function/class does one thing well; follow SOLID principles where applicable
• Error handling: Wrap all I/O and external calls in proper try/except blocks with specific exceptions; never use bare except
• Type safety: Include type hints (Python) or TypeScript types; validate inputs at boundaries
• Documentation: Add a docstring to every public function describing purpose, parameters, return value, and possible exceptions
• Edge cases: Handle empty inputs, null values, boundary conditions, and concurrent access where relevant
• Testing: Include at least 2 unit test examples that verify core functionality and one edge case
• Performance: Note any complexity trade-offs (O(n) vs O(n²)); optimize hot paths"""


def _fallback_research_prompt(user_input: str) -> str:
    topic = user_input.strip()
    return f"""**Situation**
A researcher or decision-maker needs an in-depth, evidence-based analysis of "{topic}". This is not a surface-level overview — they need the kind of rigorous, multi-perspective analysis that would inform real strategic decisions, with specific data points, named examples, and honest assessment of trade-offs.

**Task**
Produce a comprehensive research analysis on "{topic}". Structure it as: (1) Executive Summary capturing the key insight in 3 sentences, (2) Background & Context explaining why this matters now, (3) Detailed Analysis covering at least 3 major perspectives or approaches with evidence, (4) Comparative Assessment using a structured framework, (5) Recommendations with specific, actionable next steps.

**Objective**
The analysis must go significantly deeper than what a Google search would yield. Every claim should be supported by a specific example, data point, or named source. A decision-maker should be able to act on this analysis with confidence. Present both sides of any debate — one-sided analysis is unacceptable.

**Requirements**
• Depth: Cover at minimum 3 different perspectives or approaches to "{topic}", with pros and cons for each
• Evidence: Include at least 3 real-world examples, case studies, or named companies/studies as supporting evidence
• Structure: Use a comparison matrix or structured framework for any head-to-head evaluation
• Recency: Prioritize recent developments (2023–2025); flag any information that may be outdated
• Balance: Present arguments both for AND against major positions; include expert consensus AND dissenting views
• Actionability: End with 3–5 concrete, specific recommendations ranked by impact and feasibility
• Limitations: Explicitly state what the analysis does NOT cover and where evidence is weak or conflicting"""


def _fallback_text_prompt(user_input: str) -> str:
    topic = user_input.strip()
    return f"""**Situation**
You are acting as a world-class expert with 20+ years of hands-on experience in the domain of "{topic}". The user needs comprehensive, immediately actionable guidance that goes well beyond surface-level advice — they need the kind of insight you'd only get from a seasoned practitioner, not a generic article.

**Task**
Provide a deeply researched, expertly structured response on "{topic}". Break it into clearly labeled sections. For each section: explain the concept, demonstrate it with a concrete example or scenario, and connect it to real-world application. If code is involved, show working examples with inline comments.

**Objective**
The output must feel like a masterclass delivered by an expert who both deeply understands the theory AND has battle-tested it in the real world. A beginner should finish reading with a solid mental model; an intermediate reader should discover at least 3 things they didn't know. The response should be thorough enough to replace 30 minutes of Googling.

**Requirements**
• Structure: Open with a 3-sentence TL;DR that captures the core insight of "{topic}", then expand into 4–6 labeled sections with H2 headers
• Depth: Include at minimum 2 real-world examples or case studies relevant to "{topic}" — name specific tools, companies, or situations
• Accuracy: Use precise terminology; define any jargon on first use; cite specific version numbers or dates where relevant
• Practicality: Every section must end with one concrete "action item" the reader can apply immediately regarding "{topic}"
• Tone: Write like a sharp, direct senior practitioner — confident, zero fluff, no filler phrases like "great question" or "certainly"
• Scope: Address both the common path AND at least one non-obvious edge case or advanced consideration
• Closing: End with a "Top 3 Mistakes to Avoid" section with specific, experience-based pitfalls related to '{topic}'"""


# ─── System Prompt Lookup ─────────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "image": IMAGE_SYSTEM_PROMPT,
    "code": CODE_SYSTEM_PROMPT,
    "research": RESEARCH_SYSTEM_PROMPT,
    "text": TEXT_SYSTEM_PROMPT,
}

USER_MESSAGE_TEMPLATES = {
    "image": (
        "Transform this rough idea into an elite, highly detailed image generation prompt "
        "using the Situation/Task/Objective/Knowledge format. Be specific, vivid, and expert-level. "
        "Idea: {input}"
    ),
    "code": (
        "Transform this rough coding request into a precise, production-grade programming prompt "
        "using the Situation/Task/Objective/Requirements format. "
        "Specify exact technologies, architecture patterns, and quality standards. "
        "Request: {input}"
    ),
    "research": (
        "Transform this rough research question into a comprehensive, analytically rigorous research prompt "
        "using the Situation/Task/Objective/Requirements format. "
        "Ensure multi-perspective analysis with evidence standards. "
        "Question: {input}"
    ),
    "text": (
        "Transform this rough idea into a masterfully crafted AI prompt "
        "using the Situation/Task/Objective/Requirements format. "
        "Make every section concrete, specific, and immediately actionable. "
        "Idea: {input}"
    ),
}


# ─── Main Functions ────────────────────────────────────────────────────────────

def enhance_prompt(user_input: str, refinement: str = None) -> str:
    prompt_type = detect_type(user_input)
    full_input = user_input
    if refinement and refinement.strip():
        full_input = f"{user_input}\n\nAdditional context and requirements: {refinement.strip()}"

    system_prompt = SYSTEM_PROMPTS[prompt_type]
    user_message = USER_MESSAGE_TEMPLATES[prompt_type].format(input=full_input)

    if client:
        try:
            from google.genai import types
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.85,
                    max_output_tokens=1000,
                )
            )
            return response.text.strip()
        except Exception:
            pass

    # Fallback templates
    fallbacks = {
        "image": _fallback_image_prompt,
        "code": _fallback_code_prompt,
        "research": _fallback_research_prompt,
        "text": _fallback_text_prompt,
    }
    return fallbacks[prompt_type](full_input)


# ─── Fallback question banks ───────────────────────────────────────────────────

def _fallback_image_questions(topic: str) -> list:
    return [
        f"What style or medium do you prefer for '{topic}'? (e.g. photorealistic, anime, oil painting, concept art)",
        f"Any specific pose, action, or scene details for '{topic}'?",
        f"What color palette or mood are you going for? (e.g. dark and moody, vibrant, pastel)",
    ]

def _fallback_code_questions(topic: str) -> list:
    return [
        f"Should the output for '{topic}' be a complete working app or a focused code snippet?",
        f"Are there specific edge cases or error scenarios to handle for '{topic}'?",
        f"Do you need tests, documentation, or usage examples included?",
    ]

def _fallback_research_questions(topic: str) -> list:
    return [
        f"What is the primary goal of this research on '{topic}'? (e.g. decision-making, academic paper, competitive analysis)",
        f"How deep should the analysis go? (e.g. surface overview, detailed comparison, exhaustive literature review)",
        f"Are there specific perspectives, time periods, or regions to focus on?",
    ]

def _fallback_text_questions(topic: str) -> list:
    return [
        f"Who is the target audience for this content about '{topic}'?",
        f"What format do you prefer for the output? (e.g. bullet points, essay, step-by-step guide)",
        f"Any tone or length constraints? (e.g. professional, friendly, under 300 words)",
    ]


def generate_questions(user_input: str, prompt_type: str) -> list:
    """Returns 3 contextual improvement questions for the right panel."""

    # Category-specific system instructions so questions match the prompt type
    type_instructions = {
        "image": (
            "You are an image prompt refinement expert. Given a user's rough image idea, "
            "generate exactly 3 short, sharp, specific questions that would most significantly "
            "improve the final image prompt. Focus on: art style/medium, composition/lighting, "
            "color palette/mood, subject details, or camera angle. "
            "Each question on its own line, numbered 1. 2. 3. No extra text."
        ),
        "code": (
            "You are a software engineering prompt expert. Given a user's rough coding request, "
            "generate exactly 3 short, sharp, specific questions that would most significantly "
            "improve the final code prompt. Focus on: desired output format (full app vs snippet), "
            "specific features or edge cases to handle, and quality expectations (tests, docs, error handling). "
            "Each question on its own line, numbered 1. 2. 3. No extra text."
        ),
        "research": (
            "You are a research analysis prompt expert. Given a user's rough research question, "
            "generate exactly 3 short, sharp, specific questions that would most significantly "
            "improve the final research prompt. Focus on: scope/depth, time period, "
            "comparison criteria, evidence standards, or target audience for the analysis. "
            "Each question on its own line, numbered 1. 2. 3. No extra text."
        ),
        "text": (
            "You are a prompt refinement expert. Given a user's rough idea, "
            "generate exactly 3 short, sharp, specific questions that would most "
            "significantly improve the final prompt if answered. Focus on the biggest "
            "unknowns: audience, format, constraints, or domain specifics. "
            "Each question on its own line, numbered 1. 2. 3. No extra text."
        ),
    }

    if client:
        try:
            from google.genai import types
            system_inst = type_instructions.get(prompt_type, type_instructions["text"])
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"This is a {prompt_type.upper()} request. Generate 3 clarifying questions for: {user_input}",
                config=types.GenerateContentConfig(
                    system_instruction=system_inst,
                    temperature=0.7,
                    max_output_tokens=200,
                )
            )
            lines = [
                l.strip().lstrip("123456789. )")
                for l in response.text.strip().splitlines()
                if l.strip() and l.strip()[0].isdigit()
            ]
            if len(lines) >= 3:
                return lines[:3]
        except Exception:
            pass

    # Fallback: type-based question bank
    topic = user_input.strip()
    question_banks = {
        "image": lambda t: _fallback_image_questions(t.lstrip("draw ").lstrip("create ").lstrip("generate ").strip()),
        "code": _fallback_code_questions,
        "research": _fallback_research_questions,
        "text": _fallback_text_questions,
    }
    return question_banks.get(prompt_type, _fallback_text_questions)(topic)
