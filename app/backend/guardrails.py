"""
CareerBridge AI - Scope Control & Responsible AI Guardrails
General-purpose career guidance aligned with UN SDG 8.
"""
import re
from typing import Tuple, Optional
from app.backend.prompts import (
    OUT_OF_SCOPE_RESPONSE,
    GUARANTEE_REFUSAL_RESPONSE,
    FAKE_CERTIFICATE_REFUSAL_RESPONSE,
)

# Out-of-scope patterns (sports scores, creative writing, generic jokes, weather, pop culture trivia)
OUT_OF_SCOPE_PATTERNS = [
    r"\b(cricket|football|soccer|basketball|ipl|world cup|nba)\b.*\b(match|score|won|winner|playing|tournament)\b",
    r"\bwho won\b.*\b(match|game|cup|series|yesterday|today)\b",
    r"\b(write|recite|make)\b.*\b(poem|poetry|rhyme|song|ballad|haiku)\b",
    r"\b(tell|crack)\b.*\b(joke|riddle|funny story)\b",
    r"\bwhat('s| is) the weather\b",
    r"\b(will it rain|forecast for tomorrow|temperature in)\b",
    r"\b(movie|film|tv show|anime)\b.*\b(spoiler|recommendation|review|actor|actress)\b",
    r"\bwho is (batman|superman|spiderman|iron man|captain america)\b",
    r"\b(horoscope|astrology|zodiac sign)\b",
    r"\bwhat is the capital of\b",
    r"\bwho (is|was) the (president|monarch|king|queen) of\b(?!.*(?:civil services|upsc|exam|gk))",
    r"\bhow tall is\b",
    r"\bwho invented\b(?!.*(?:history of|exam|study))",
]

# Broad career, education, and employability keywords across diverse disciplines
CAREER_DOMAIN_KEYWORDS = [
    # General career & employability terms
    "career", "job", "internship", "resume", "cv", "interview", "workplace", "employability",
    "soft skills", "communication", "salary", "fresher", "decent work", "sdg", "sdg 8", "economic",
    "roadmap", "learn", "study", "skills", "profession", "licensing", "exam", "college", "university",
    "graduation", "after 12th", "what should i do", "what are employability skills", "what is an internship",
    "what is a resume", "how do i prepare", "how to prepare", "how to choose", "choose a career",
    "find my strengths", "what is decent work", "what does sdg 8 mean", "first job", "no experience",

    # Engineering & Technology
    "civil engineer", "civil engineering", "mechanical engineer", "mechanical engineering",
    "electrical engineer", "electrical engineering", "electronics", "chemical engineer", "aerospace",
    "biomedical", "autocad", "solidworks", "cad", "cam", "staad pro", "revit", "surveying", "thermodynamics",
    "python", "java", "c++", "javascript", "golang", "rust", "sql", "html", "css", "react", "node",
    "machine learning", "deep learning", "data science", "data analysis", "ai", "artificial intelligence",
    "linkedin", "github", "git", "docker", "kubernetes", "cloud", "aws", "azure", "cybersecurity",

    # Healthcare & Medicine
    "doctor", "medicine", "medical", "mbbs", "physician", "surgeon", "neet", "bds", "dentist",
    "nursing", "nurse", "pharmacy", "pharmacist", "clinical", "hospital", "healthcare", "patient care",

    # Law & Legal
    "lawyer", "law", "advocate", "llb", "legal", "judiciary", "bar exam", "clat", "moot court",
    "attorney", "legal research", "statutory", "litigation", "corporate law",

    # Education & Teaching
    "teacher", "teaching", "educator", "professor", "lecturer", "b.ed", "pedagogy", "curriculum",
    "classroom management", "tutor", "school teacher", "faculty",

    # Architecture & Design
    "architect", "architecture", "b.arch", "interior design", "interior designer", "graphic design",
    "graphic designer", "ui/ux", "designer", "figma", "photoshop", "illustrator", "typography",
    "branding", "design portfolio", "animation",

    # Finance, Accounting & Business
    "finance", "financial", "accounting", "accountant", "chartered accountant", "ca", "banking",
    "banker", "cfa", "investment banking", "financial modeling", "economics", "commerce", "mba",
    "marketing", "human resources", "hr", "audit", "tally",

    # Government & Public Sector
    "government job", "government jobs", "public sector", "upsc", "civil services", "ias", "ips",
    "ssc", "banking exam", "ibps", "nda", "cds", "defence", "state psc", "sarkari",

    # Multilingual triggers (Hindi & Gujarati)
    "banna", "chahta", "chahti", "banva", "maangu", "banvu", "naukri", "kaam", "rozgar"
]

# Safety triggers: Job / Placement / Salary Guarantees
GUARANTEE_PATTERNS = [
    r"\b(can you|do you|will you)\b.*\bguarantee\b.*\b(job|placement|salary|internship|hire|hired|offer)\b",
    r"\bguarantee\b.*\b(i will get|me a job|a job|100% placement|employment|salary)\b",
    r"\bpromise\b.*\b(job|placement|salary|internship)\b",
    r"\bconfirm that i will get hired\b",
]

# Safety triggers: Fake certificates / Fraudulent credentials / Resume lies
FRAUD_PATTERNS = [
    r"\b(fake|falsified|counterfeit|bogus|forge|forged|dummy)\b.*\b(certificate|cert|internship certificate|degree|diploma|experience letter|document)\b",
    r"\b(give|make|generate|create|provide)\b.*\b(fake|counterfeit)\b",
    r"\b(lie|falsify|cheat)\b.*\b(on (my )?resume|in (an )?interview|background check|cv)\b",
    r"\bbuy\b.*\b(fake|illegal)\b.*\b(certificate|experience)\b",
]

# Discrimination or exploitation patterns
EXPLOITATION_PATTERNS = [
    r"\b(discriminate|filter out|reject)\b.*\b(based on|due to)\b.*\b(caste|gender|religion|race|disability)\b",
    r"\b(work without pay|unpaid forever|slave labor|unsafe conditions)\b",
]

def check_guardrails(message: str) -> Tuple[bool, Optional[str]]:
    """
    Checks the user message against Responsible AI guardrails and scope rules.
    Returns:
        (is_handled: bool, response: Optional[str])
        If is_handled is True, response contains the compliant reply to return immediately.
        If is_handled is False, the query is safe and within scope to process further.
    """
    cleaned = message.strip().lower()

    if not cleaned:
        return True, "Your message appears to be empty. Please ask a career, education, skill, or workplace question!"

    # 1. Safety Check: Fraudulent credentials / Fake certificates
    for pattern in FRAUD_PATTERNS:
        if re.search(pattern, cleaned):
            return True, FAKE_CERTIFICATE_REFUSAL_RESPONSE

    # 2. Safety Check: Employment / Salary guarantees
    for pattern in GUARANTEE_PATTERNS:
        if re.search(pattern, cleaned):
            return True, GUARANTEE_REFUSAL_RESPONSE

    # 3. Safety Check: Discrimination & Exploitation
    for pattern in EXPLOITATION_PATTERNS:
        if re.search(pattern, cleaned):
            return True, (
                "CareerBridge AI operates strictly within UN SDG 8 principles, promoting inclusive, non-discriminatory, "
                "safe, and fair workplace standards. I cannot provide recommendations that encourage discrimination or exploitative labor."
            )

    # 4. Out-of-Scope Check (sports scores, poetry, jokes, weather, geography trivia)
    for pattern in OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, cleaned):
            if ("poem" in cleaned or "joke" in cleaned) and ("interview" in cleaned or "career" in cleaned or "resume" in cleaned):
                pass
            else:
                if "capital of" in cleaned:
                    return True, (
                        "I'm primarily designed for career, education, employability, and SDG 8 guidance. "
                        "I can help with career-related questions such as choosing a field, skills, resumes, internships, and interviews.\n\n"
                        "How can I assist your career or educational journey today?"
                    )
                return True, OUT_OF_SCOPE_RESPONSE

    # 5. Check if the message has clear career, education, or skill relevance
    has_career_relevance = False
    for kw in CAREER_DOMAIN_KEYWORDS:
        if len(kw) <= 3:
            if re.search(r"\b" + re.escape(kw) + r"\b", cleaned):
                has_career_relevance = True
                break
        elif kw in cleaned:
            has_career_relevance = True
            break

    # If the user asks pure non-career chit-chat like sports results
    if re.search(r"\b(cricket|football|match|score)\b", cleaned) and not has_career_relevance:
        return True, OUT_OF_SCOPE_RESPONSE

    return False, None
