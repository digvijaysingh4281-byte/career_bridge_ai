"""
CareerBridge AI - Conversational Core & General Career Knowledge Engine
General-purpose career guidance aligned with UN SDG 8: Decent Work and Economic Growth.
Supports Engineering, Healthcare, Law, Teaching, Design, Finance, Public Sector, Trades, and Tech.
"""
import os
import re
import logging
from typing import Dict, Any, Tuple, Optional, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("careerbridge.chatbot")

from app.backend.prompts import (
    SYSTEM_PROMPT,
    INTERVIEW_MODE_PROMPT,
    RESUME_REVIEW_PROMPT,
    OUT_OF_SCOPE_RESPONSE,
)
from app.backend.guardrails import check_guardrails
from app.backend.memory import memory_store
from app.utils.snapshot import generate_readiness_snapshot

# Check configured API keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
GENERIC_LLM_KEY = os.environ.get("LLM_API_KEY", "").strip()

INTERVIEW_QUESTION_BANKS = {
    "civil engineering": [
        "Tell me about a civil engineering project, drawing, or design assignment you worked on. What structural or material challenges did you address?",
        "How do you ensure construction quality, material compliance (like concrete slump and curing), and safety standards on an active civil worksite?",
        "Can you explain the key differences between shallow and deep foundations, and how soil bearing capacity influences your choice?",
        "How do you use software tools like AutoCAD, STAAD Pro, or Revit for structural modeling and drafting?",
        "How do you handle site disputes or discrepancies between architectural drawings and structural engineering constraints?"
    ],
    "mechanical engineering": [
        "Tell me about a mechanical component, system, or mechanism you designed or analyzed. What engineering tools and principles guided your choices?",
        "Can you explain the primary differences between the Otto cycle and Diesel cycle, and what practical factors govern their thermal efficiency?",
        "How do you determine appropriate material selection, safety factors, and manufacturing tolerances for a part subject to dynamic fatigue?",
        "What is your diagnostic process when a mechanical prototype, bearing, or welded joint fails unexpected stress testing?",
        "How do modern CAD/CAM and automated manufacturing processes support safe, sustainable industrial production under SDG 8?"
    ],
    "doctor": [
        "Walk me through your clinical approach to examining and taking the medical history of a patient presenting with acute fever and chest pain.",
        "In an emergency or outpatient department, how do you prioritize triage when multiple patients require urgent attention simultaneously?",
        "How do you communicate sensitive clinical diagnoses or difficult prognoses to a patient and their distressed family members?",
        "Can you discuss a clinical or academic scenario where patient confidentiality and medical ethics guided your decision-making?",
        "How do you stay abreast of evidence-based medical research, diagnostic protocols, and pharmacology updates?"
    ],
    "medicine": [
        "Walk me through your clinical approach to patient history-taking and differential diagnosis for acute abdominal distress.",
        "How do you balance rapid clinical decision-making with patient safety during high-pressure hospital rotations?",
        "How do you address treatment compliance challenges with patients from diverse socio-economic backgrounds?",
        "Can you discuss the ethical principles of informed consent and patient autonomy in medical practice?",
        "What clinical specialization or healthcare area are you aspiring to pursue, and why?"
    ],
    "pharmacist": [
        "How do you evaluate prescriptions for drug-drug interactions, appropriate dosages, and contraindications before dispensing?",
        "Describe your approach to patient counseling regarding medication adherence, administration instructions, and potential side effects.",
        "How do you ensure strict compliance with pharmacy laws, narcotic/controlled substance documentation, and storage requirements?",
        "Walk me through a situation where a prescription seemed ambiguous or potentially harmful. How did you communicate with the prescribing physician?",
        "How do you maintain accurate inventory control, cold-chain integrity, and prevent expired stock in a hospital or retail pharmacy?"
    ],
    "pharmacy": [
        "What is your understanding of pharmacokinetics and pharmacodynamics, and how do they inform dosage regimen design?",
        "How do you approach compounding, sterile preparation, and quality assurance in a pharmaceutical or clinical laboratory setting?",
        "How do you explain complex pharmacological information to patients with limited health literacy to ensure safe medication use?",
        "What are the key regulatory standards (e.g., FDA, Good Manufacturing Practices - GMP, Pharmacy Council) governing drug quality and safety?",
        "Tell me about a time you identified a clinical error, dispensing discrepancy, or adverse drug reaction, and the steps you took to resolve it."
    ],
    "btech cse": [
        "Can you explain the time and space complexity trade-offs between QuickSort and MergeSort, and when you would prefer one over the other?",
        "Walk me through how an HTTP GET request travels from browser URL entry to DNS lookup, TCP handshake, server processing, database query, and response rendering.",
        "How do you design a normalized relational database schema (3NF), and in what scenarios might you intentionally introduce denormalization or caching?",
        "Describe a major project or technical challenge you tackled during your B.Tech CSE coursework. What architecture choices and debugging strategies did you employ?",
        "How do you ensure secure, ethical coding practices (such as input validation, SQL injection prevention, and data privacy) in line with sustainable software engineering?"
    ],
    "cse": [
        "Explain the core differences between a process and a thread, and how multithreading is synchronized to prevent race conditions and deadlocks.",
        "Walk me through your problem-solving approach to a complex Data Structures & Algorithms problem on arrays, trees, or dynamic programming.",
        "How do you use Git branching strategies, pull requests, and code reviews when collaborating on a team project?",
        "What are the foundational principles of Object-Oriented Programming (OOP), and how have you applied polymorphism or encapsulation in your code?",
        "Can you discuss a software bug you encountered that was difficult to diagnose, and how you traced root causes using logging and debuggers?"
    ],
    "lawyer": [
        "Walk me through how you conduct legal research on a complex statutory or constitutional issue using case law databases and legal precedents.",
        "How do you approach drafting a formal legal notice, contract clause, or written statement to minimize ambiguity and protect client interests?",
        "Can you analyze a recent landmark judicial precedent and explain how it shapes current jurisprudence in that field?",
        "How do you navigate situations where a client's requests conflict with bar council professional ethics and court duty?",
        "Tell me about your experience in moot court arguments, trial advocacy, or chamber internships."
    ],
    "law": [
        "How do you analyze statutory provisions and distinguish binding judicial precedents from obiter dicta?",
        "Walk me through your strategy for preparing a case brief and legal arguments for a contested hearing.",
        "How do you manage client expectations while providing an objective assessment of legal risks and litigation costs?",
        "What are the ethical responsibilities of an advocate regarding truthfulness before the court and attorney-client privilege?",
        "Tell me about an area of law (constitutional, corporate, criminal, IP, or arbitration) that interests you most and why."
    ],
    "teacher": [
        "How do you design a comprehensive lesson plan that accommodates diverse student learning paces, backgrounds, and abilities?",
        "Describe your classroom management philosophy: how do you foster mutual respect and address disruptive behavior constructively?",
        "How do you assess student conceptual understanding beyond standard examinations and rote memorization?",
        "Tell me about a time you helped an unmotivated or struggling student achieve meaningful academic or personal growth.",
        "How do you integrate modern educational technology and interactive teaching methodologies into your classroom?"
    ],
    "teaching": [
        "How do you tailor pedagogical techniques to make complex subjects accessible and engaging for learners?",
        "How do you build an inclusive, supportive learning environment that promotes student curiosity and critical thinking?",
        "What strategies do you use for formative assessment and constructive student feedback during a term?",
        "How do you collaborate with parents, school administration, and colleagues to support student well-being?",
        "What does lifelong learning mean to you as an educator advancing quality education under sustainable development goals?"
    ],
    "graphic designer": [
        "Walk me through your design process from initial creative brief and mood board exploration to final asset delivery.",
        "How do you approach typography selection, grid hierarchy, and color harmony to effectively communicate a brand's message?",
        "How do you handle critical feedback or design revisions from stakeholders whose preferences diverge from design best practices?",
        "What design software (Figma, Illustrator, Photoshop, InDesign) do you rely on most, and how do you ensure cross-media consistency?",
        "Can you discuss a portfolio project you are proud of, explaining the problem it solved and the creative choices you made?"
    ],
    "graphic design": [
        "How do you establish visual hierarchy and user empathy when designing promotional or digital interface materials?",
        "Walk me through how you organize design systems, components, and export specifications for production handoff.",
        "How do you balance creative visual exploration with strict client brand guidelines and project deadlines?",
        "Describe your approach to receiving design critiques and iterating on visual concepts based on user feedback.",
        "What industry trends in visual design, typography, or UI/UX are currently influencing your work?"
    ],
    "finance": [
        "How do the three primary financial statements (Income Statement, Balance Sheet, Cash Flow Statement) link together analytically?",
        "Walk me through how you construct a discounted cash flow (DCF) model or evaluate capital budgeting decisions using NPV and IRR.",
        "How do you evaluate a company's working capital health, liquidity ratios, and debt serviceability?",
        "Tell me about a time you used advanced Excel, financial modeling, or analytical tools to extract actionable business insights.",
        "How does transparent financial reporting and ethical stewardship support sustainable corporate governance and decent work (SDG 8)?"
    ],
    "government": [
        "What motivates your dedication to civil services and public sector governance, and how do you envision serving the community?",
        "How would you approach a situation where public policy implementation faces resistance from local socio-economic groups?",
        "How do you maintain strict ethical neutrality, integrity, and public accountability when handling administrative decisions?",
        "Discuss a major contemporary socio-economic challenge (e.g. youth employability, rural infrastructure) and your proposed policy intervention.",
        "How do you organize your preparation strategy, syllabus coverage, and revision discipline for multi-stage competitive examinations?"
    ],
    "general": [
        "Tell me about a significant academic assignment, professional task, or project you completed. What was your role and the outcome?",
        "How do you prioritize competing deadlines and manage high-pressure situations effectively?",
        "Describe a time you collaborated with team members holding divergent viewpoints or working styles to achieve a common goal.",
        "Tell me about a time you had to learn a completely new domain, tool, or methodology quickly.",
        "How do you maintain professional integrity, accountability, and workplace safety in your daily responsibilities?"
    ]
}

def get_interview_questions_for_role(role: str) -> List[str]:
    """Retrieves field-specific interview questions based on the active role or career goal."""
    norm = role.lower().strip()
    for key, questions in INTERVIEW_QUESTION_BANKS.items():
        if key in norm or norm in key:
            return questions
    return INTERVIEW_QUESTION_BANKS["general"]

def format_context_prompt(context: Dict[str, Any]) -> str:
    """Formats the active user profile for context injection."""
    parts = []
    if context.get("education_level"):
        parts.append(f"- Education Level: {context['education_level']}")
    if context.get("field"):
        parts.append(f"- Field of Study: {context['field']}")
    if context.get("career_interest") or context.get("career_goal"):
        goal = context.get("career_interest") or context.get("career_goal")
        parts.append(f"- Active Career Goal / Target Field: {goal}")
    if context.get("skills"):
        parts.append(f"- Known Skills: {', '.join(context['skills'])}")
    if context.get("experience_level"):
        parts.append(f"- Stated Experience: {context['experience_level']}")

    if not parts:
        return "No specific prior profile provided yet. Maintain welcoming, career-inclusive tone across all professions."
    return "\n".join(parts)

def generate_local_engine_response(message: str, session_id: str, context: Dict[str, Any], history: List[Dict[str, str]]) -> str:
    """
    General-purpose career guidance knowledge engine.
    Supports Engineering (Civil, Mechanical, Electrical), Healthcare (Doctor, Medicine),
    Law, Teaching, Design, Finance, Public Sector, Trades, and General Employability.
    """
    text = message.strip()
    lower = text.lower()

    active_career = context.get("career_interest") or context.get("career_goal") or ""
    edu = context.get("education_level") or ""
    skills = context.get("skills") or []

    # 1. Interview Mode handling
    if context.get("interview_mode"):
        q_idx = context.get("interview_question_idx", 1)
        role = context.get("interview_role") or active_career or "General Career"
        question_bank = get_interview_questions_for_role(role)

        # Initial interview start
        if any(w in lower for w in ["interview me", "mock interview", "take my", "prepare an interview"]):
            memory_store.update_user_context(session_id, interview_mode=1, interview_question_idx=1, interview_role=role)
            first_q = question_bank[0]
            return (
                f"### 🎤 Mock Interview Started: **{role.title()}**\n\n"
                f"Welcome! We will proceed one question at a time tailored specifically to **{role.title()}**. "
                f"After your response, I will evaluate your answer, note key strengths, offer actionable improvements, "
                f"share a model answer, and ask the next question.\n\n"
                f"**Question 1:**\n> {first_q}\n\n"
                f"*Take your time to structure a thoughtful, professional response!*"
            )

        eval_idx = min(q_idx - 1, len(question_bank) - 1)
        prev_q = question_bank[eval_idx]
        next_idx = q_idx + 1

        if q_idx < len(question_bank):
            memory_store.update_user_context(session_id, interview_question_idx=next_idx)
            next_q = question_bank[q_idx]

            return (
                f"### 📋 Feedback on Question {q_idx} ({role.title()})\n\n"
                f"**Question:** *{prev_q}*\n\n"
                f"**What was good:**\n"
                f"• Direct engagement with the core technical/operational requirements of the question.\n"
                f"• Good display of domain terminology and professional thought process.\n\n"
                f"**Constructive Improvement:**\n"
                f"• Structure responses using the **STAR Method** (Situation, Task, Action, Result) to provide concrete evidence of capability.\n"
                f"• Clearly highlight how your decisions ensure quality, safety, and compliance with industry standards.\n\n"
                f"**Stronger Example Phrasing:**\n"
                f"> *\"In my prior project, when faced with unexpected material/design constraints, I conducted a thorough root-cause "
                f"analysis, consulted industry standards, and collaborated with the team to deliver an optimized, compliant solution on schedule.\"*\n\n"
                f"---\n\n"
                f"**Question {next_idx}:**\n"
                f"> {next_q}"
            )
        else:
            memory_store.update_user_context(session_id, interview_mode=0, interview_question_idx=0)
            return (
                f"### 🏁 Mock Interview Completed: **{role.title()}**!\n\n"
                f"Congratulations on completing your interview simulation for **{role.title()}**! "
                f"Practicing structured, confident communication is essential for career success.\n\n"
                f"**Key Takeaways:**\n"
                f"1. **Domain Precision:** Continue backing up your answers with specific technical methodologies and standards.\n"
                f"2. **Workplace Ethics:** Highlighting safety, honesty, and team communication aligns directly with SDG 8 decent work principles.\n"
                f"3. **Next step:** Would you like to review your resume, explore internships, or practice another career topic?"
            )

    # 2. General Career & Employability Concepts
    if "what are employability skills" in lower or "employability skills" in lower:
        return (
            "### 🌟 Essential Employability Skills for the Modern Workplace\n\n"
            "**Employability skills** (also known as foundational or transferable skills) are the essential non-technical competencies "
            "that enable professionals to succeed across all industries, from engineering and healthcare to law, finance, and education:\n\n"
            "1. **Professional Communication:** Clear oral articulation, active listening, and structured written documentation.\n"
            "2. **Critical Thinking & Problem-Solving:** The ability to analyze facts, evaluate evidence, and design practical solutions.\n"
            "3. **Teamwork & Collaboration:** Working respectfully with cross-functional and diverse colleagues.\n"
            "4. **Adaptability & Lifelong Learning:** Eagerness to update knowledge as tools and regulations evolve.\n"
            "5. **Digital & Information Literacy:** Comfort using modern productivity tools, research databases, and domain software.\n"
            "6. **Professional Ethics & Reliability:** Accountability, time discipline, and adherence to workplace safety standards.\n\n"
            "**SDG 8 Connection:** Developing robust employability skills enhances productive employment, job retention, and sustainable economic participation.\n\n"
            "**Next step:** What specific profession or industry are you planning to enter?"
        )

    if "what is an internship" in lower:
        return (
            "### 🎓 What is an Internship & Why It Matters\n\n"
            "An **internship** is a structured period of hands-on professional work experience offered by employers to students, "
            "fresh graduates, and career switchers to bridge academic theory and real-world workplace practice.\n\n"
            "#### Why Internships are Critical:\n"
            "• **Practical Experience:** Apply textbook knowledge to actual industrial, clinical, legal, or commercial tasks.\n"
            "• **Professional Mentorship:** Learn directly from experienced practitioners in your field.\n"
            "• **Networking & References:** Build relationships that often lead to full-time employment offers.\n"
            "• **Resume Enhancement:** Demonstrates verified workplace readiness to prospective employers.\n\n"
            "**SDG 8 Standard:** High-quality internships should provide legitimate learning opportunities, safe working conditions, "
            "and fair compensation, avoiding exploitative unpaid labor.\n\n"
            "**Next step:** Tell me your field of study, and I will outline the most valuable types of internships for your domain!"
        )

    if "what is a resume" in lower or "what is a cv" in lower:
        return (
            "### 📄 What is a Resume & How It Works\n\n"
            "A **resume** (or Curriculum Vitae / CV) is a concise, formal document that summarizes your educational background, "
            "practical skills, relevant work experience, projects, and key achievements for prospective employers.\n\n"
            "#### Core Elements of an Effective Resume:\n"
            "1. **Header:** Contact information, professional email, and professional profile link (e.g. LinkedIn or portfolio).\n"
            "2. **Education:** Degrees, institution, graduation year, and academic achievements.\n"
            "3. **Skills Section:** Grouped by technical/domain competencies and relevant tools.\n"
            "4. **Practical Experience / Projects:** Verifiable internships, clinical postings, site work, or independent projects with measurable results.\n"
            "5. **Certifications & Licensures:** Official credentials and accredited qualifications.\n\n"
            "**Next step:** Would you like guidance on drafting your resume or reviewing your existing resume draft?"
        )

    if "what is decent work" in lower or "what does sdg 8 mean" in lower or "why sdg 8" in lower:
        return (
            "### 🌍 Understanding UN SDG 8: Decent Work & Economic Growth\n\n"
            "**UN Sustainable Development Goal 8 (SDG 8)** aims to *'Promote sustained, inclusive and sustainable economic growth, "
            "full and productive employment and decent work for all.'*\n\n"
            "#### What Defines 'Decent Work'?\n"
            "• **Productive Employment:** Fair opportunities for individuals to apply their talents and earn a living wage.\n"
            "• **Workplace Safety & Health:** Safe physical working conditions free from occupational hazards and exploitation.\n"
            "• **Equal Opportunity & Non-Discrimination:** Merit-based hiring without bias based on gender, race, disability, or background.\n"
            "• **Continuous Learning:** Access to skill upgrading, apprenticeships, and professional development.\n"
            "• **Social Protection & Dignity:** Respect for labor rights, voice in the workplace, and social security.\n\n"
            "CareerBridge AI supports SDG 8 by democratizing career guidance, demystifying skill roadmaps, and empowering ethical professional readiness.\n\n"
            "**Next step:** How can I assist you with your career planning or employability preparation today?"
        )

    if "what is machine learning" in lower or "what is ml" in lower:
        return (
            "### 🤖 Machine Learning Explained (Career & Learning Context)\n\n"
            "**Machine Learning (ML)** is a computational field where algorithms learn patterns from data "
            "to make predictions or decisions without being explicitly programmed for every scenario.\n\n"
            "#### Career & Skill Applications:\n"
            "• **Key Roles:** ML Engineer, Data Scientist, Research Scientist, Business Intelligence Analyst.\n"
            "• **Core Skills Needed:** Mathematics (linear algebra, calculus, statistics), Python, and libraries (Scikit-Learn, PyTorch).\n"
            "• **Practical Applications:** Healthcare imaging, algorithmic fraud detection, predictive maintenance, and autonomous systems.\n\n"
            "**SDG 8 Connection:** Developing productive digital skills drives modern technological innovation and high-quality employment.\n\n"
            "**Next step:** Would you like to explore the foundational roadmap for machine learning and data science?"
        )

    if "what is linkedin" in lower or ("linkedin" in lower and any(w in lower for w in ["what", "how", "purpose"])):
        return (
            "### 🌐 What is LinkedIn & Why It Matters for Your Career\n\n"
            "**LinkedIn** is the world's largest professional networking platform. For students, fresh graduates, and professionals, "
            "it functions as a living digital resume, professional portfolio, and career discovery engine.\n\n"
            "#### Key Benefits for Job Seekers:\n"
            "1. **Professional Networking:** Connect directly with alumni, industry mentors, and hiring managers in your field.\n"
            "2. **Job & Internship Discovery:** Access verified job openings with company insights and application tracking.\n"
            "3. **Showcasing Projects & Credentials:** Publish updates on academic projects, certifications, and technical accomplishments.\n"
            "4. **Industry Learning:** Follow thought leaders, companies, and industry developments to understand labor market trends.\n\n"
            "**SDG 8 Connection:** Open professional networks democratize access to economic opportunities and transparent hiring.\n\n"
            "**Next step:** Would you like actionable advice on optimizing your LinkedIn headline and profile summary?"
        )

    if any(w in lower for w in ["prepare for my first interview", "prepare for an interview", "prepare for interview", "first interview prep", "interview preparation", "how do i prepare for an interview", "how do i prepare for my first interview"]):
        return (
            "### 🎯 How to Prepare for Your First Job or Internship Interview\n\n"
            "Preparing thoroughly for your first interview turns anxiety into quiet confidence. Here is a proven, step-by-step preparation strategy:\n\n"
            "#### 1. Research the Organization & Role (Before the Interview)\n"
            "• **Study the Job Description:** Highlight key responsibilities and required skills. Think of 1–2 real examples where you demonstrated each skill.\n"
            "• **Company Background:** Understand what the organization does, their products/services, mission, and recent news.\n\n"
            "#### 2. Master the STAR Technique for Behavioral Questions\n"
            "When asked about past experiences or challenges, structure your answers using:\n"
            "• **S - Situation:** Briefly set the context.\n"
            "• **T - Task:** Explain what needed to be accomplished.\n"
            "• **A - Action:** Describe the specific steps YOU took.\n"
            "• **R - Result:** Share the positive, measurable outcome.\n\n"
            "#### 3. Prepare Answers to Standard Opening Questions\n"
            "• *'Tell me about yourself':* Focus on your educational background, relevant skills/projects, and enthusiasm for this role.\n"
            "• *'What are your strengths?':* Name 2–3 strengths backed by concrete academic, project, or extracurricular examples.\n"
            "• *'Why do you want this role?':* Connect your career goals with the team's work.\n\n"
            "#### 4. Prepare Thoughtful Questions for the Interviewer\n"
            "Always ask 2–3 questions at the end, such as:\n"
            "• *'What does a typical day look like for someone in this position?'*\n"
            "• *'What are the most important priorities for this role in the first 90 days?'*\n\n"
            "#### 5. Professional Demeanor & SDG 8 Values\n"
            "• Punctuality, honest communication, and respectful engagement reflect core workplace ethics.\n\n"
            "**Next step:** Would you like to practice a mock interview right now? Just say 'Take my mock interview'!"
        )

    if any(w in lower for w in ["find my strengths", "identify my strengths", "what are my strengths", "strengths and weaknesses"]):
        return (
            "### 💡 How to Identify Your Professional Strengths\n\n"
            "Discovering your authentic strengths is foundational to making informed career decisions and succeeding in interviews:\n\n"
            "1. **Audit Your Past Wins:** Review projects, assignments, or activities where you excelled or felt energized. Did you excel at problem-solving, detailed analysis, organizing tasks, or team coordination?\n"
            "2. **Seek External Feedback:** Ask trusted professors, mentors, or peer teammates: *'What do you think I do most naturally and effectively?'*\n"
            "3. **Evaluate Your Learning Speed:** Notice subjects or technical tools you pick up unusually fast compared to peers. Rapid absorption indicates natural aptitude.\n"
            "4. **Categorize Technical vs. Transferable:**\n"
            "   • *Hard/Domain Skills:* Laboratory testing, software coding, drafting, financial calculation.\n"
            "   • *Soft/Interpersonal Skills:* Active listening, clear explanation, conflict resolution, time discipline.\n"
            "5. **Match with Labor Market Demand:** Align your top strengths with professions that prioritize them under decent work standards (SDG 8).\n\n"
            "**Next step:** What subjects, tools, or types of activities do you enjoy working on the most?"
        )

    # 3. Handling "What skills should I learn?"
    if re.search(r"\bwhat skills (should|do) i (learn|need)\b", lower) or lower.strip() in ["what skills should i learn", "what skills should i learn?"]:
        if active_career:
            # Profession-specific skills
            norm_c = active_career.lower()
            if "civil" in norm_c:
                return (
                    "### 🏗️ Essential Skills for Civil Engineering\n\n"
                    "To build a strong, employable profile in **Civil Engineering**, focus on these core competencies:\n\n"
                    "1. **Computer-Aided Design & Drafting:** Master **AutoCAD** and **BIM / Autodesk Revit** for 2D drafting and 3D architectural modeling.\n"
                    "2. **Structural Analysis Software:** Learn **STAAD Pro**, **ETABS**, or **SAP2000** for analyzing beams, columns, and structural loading.\n"
                    "3. **Geotechnical & Surveying:** Field surveying using **Total Station** and GPS, soil testing, and bearing capacity analysis.\n"
                    "4. **Project Management & Estimation:** Quantity surveying, rate analysis, and scheduling tools like **MS Project** or **Primavera**.\n"
                    "5. **Codes & Safety Standards:** Familiarity with national building codes (e.g. IS codes, ACI, Eurocodes) and site safety standards (SDG 8).\n\n"
                    "**Next step:** Which area of civil engineering (Structural, Geotechnical, Transportation, or Construction Management) interests you most?"
                )
            elif "mech" in norm_c:
                return (
                    "### ⚙️ Essential Skills for Mechanical Engineering\n\n"
                    "To build a competitive career in **Mechanical Engineering**, develop these critical capabilities:\n\n"
                    "1. **3D CAD & Modeling:** Proficiency in **SolidWorks**, **CATIA**, or **Autodesk Inventor** for part and assembly design.\n"
                    "2. **Finite Element Analysis (FEA) & Simulation:** **ANSYS** or **SolidWorks Simulation** for stress, thermal, and modal analysis.\n"
                    "3. **Manufacturing & Automation:** CNC programming, GD&T (Geometric Dimensioning and Tolerancing), and additive manufacturing basics.\n"
                    "4. **Thermodynamics & Fluid Power:** Practical understanding of HVAC, hydraulics, pneumatics, and energy conversion systems.\n"
                    "5. **Quality & Lean Standards:** Six Sigma, 5S, Kaizen, and industrial safety compliance (SDG 8).\n\n"
                    "**Next step:** Would you like a roadmap focused on Design Engineering, Manufacturing, or Thermal Systems?"
                )
            elif "doctor" in norm_c or "medicine" in norm_c:
                return (
                    "### 🩺 Essential Competencies for Medicine & Healthcare\n\n"
                    "Pursuing a career in **Medicine** requires a rigorous blend of clinical mastery, scientific acumen, and human empathy:\n\n"
                    "1. **Foundational Sciences:** Mastery of Human Anatomy, Physiology, Biochemistry, Pharmacology, and Pathology.\n"
                    "2. **Clinical Diagnostic Skills:** Patient history-taking, physical examination, and interpretation of diagnostic lab reports/imaging.\n"
                    "3. **Emergency & Triage Care:** Basic Life Support (BLS), Advanced Cardiovascular Life Support (ACLS), and trauma stabilization.\n"
                    "4. **Empathetic Communication:** Active listening, patient counseling, and breaking difficult clinical news with sensitivity.\n"
                    "5. **Medical Ethics & Law:** Informed consent, patient confidentiality (HIPAA / NMC guidelines), and ethical medical decision-making.\n\n"
                    "**Next step:** Are you preparing for entrance examinations (e.g. NEET/MCAT) or currently in medical school?"
                )
            elif "law" in norm_c:
                return (
                    "### ⚖️ Essential Skills for a Career in Law\n\n"
                    "A successful legal professional requires deep analytical rigor, research capability, and persuasive communication:\n\n"
                    "1. **Legal Research:** Finding precedents and statutory interpretations using platforms like SCC Online, Manupatra, or Westlaw.\n"
                    "2. **Legal Drafting:** Drafting pleadings, contracts, writ petitions, legal notices, and conveyance deeds.\n"
                    "3. **Oral Advocacy & Moot Court:** Articulating persuasive legal arguments and responding spontaneously to judicial bench queries.\n"
                    "4. **Case Law Analysis:** Synthesizing facts, identifying the ratio decidendi, and distinguishing conflicting precedents.\n"
                    "5. **Professional Ethics & Negotiation:** Alternative Dispute Resolution (ADR), mediation, and strict adherence to Bar Council ethics.\n\n"
                    "**Next step:** Do you plan to pursue Litigation, Corporate Law, or Judicial Services?"
                )
            elif "teach" in norm_c:
                return (
                    "### 📚 Essential Skills for Modern Educators & Teachers\n\n"
                    "Excellence in **Teaching & Education** goes far beyond subject knowledge:\n\n"
                    "1. **Subject-Matter Depth:** Comprehensive conceptual command of your chosen discipline.\n"
                    "2. **Pedagogy & Instructional Design:** Structuring lesson plans using differentiated instruction for varied learning paces.\n"
                    "3. **Classroom Management:** Creating an inclusive, respectful, and productive learning atmosphere.\n"
                    "4. **Formative Assessment:** Evaluating student comprehension through diverse diagnostic methods rather than rote memory alone.\n"
                    "5. **Educational Technology:** Leveraging digital classroom management systems, interactive visual aids, and hybrid tools.\n\n"
                    "**Next step:** Are you targeting primary, secondary, or higher education / university lectureship?"
                )
            elif "design" in norm_c:
                return (
                    "### 🎨 Essential Skills for Graphic & Visual Design\n\n"
                    "Building a sustainable design career requires both artistic principles and digital tool proficiency:\n\n"
                    "1. **Design Fundamentals:** Typography, visual hierarchy, color theory, layout grids, and composition.\n"
                    "2. **Industry Software:** Adobe Photoshop (photo editing), Illustrator (vector graphics), InDesign (publishing), and Figma (UI/UX).\n"
                    "3. **Branding & Visual Identity:** Crafting coherent logo systems, brand guidelines, and visual assets.\n"
                    "4. **Portfolio Development:** Showcasing curated case studies with problem statements, process sketches, and outcomes on Behance or Dribbble.\n"
                    "5. **Client Communication:** Interpreting creative briefs, articulating design rationale, and handling revisions constructively.\n\n"
                    "**Next step:** Would you like tips on organizing your first design portfolio?"
                )
            elif "finance" in norm_c:
                return (
                    "### 💼 Essential Skills for Finance & Banking\n\n"
                    "To build a strong career in **Finance & Accounting**, focus on these core capabilities:\n\n"
                    "1. **Advanced Financial Modeling:** Building 3-statement projection models, DCF valuations, and sensitivity tables in Excel.\n"
                    "2. **Financial Reporting & Analysis:** Understanding IFRS/GAAP standards, ratio analysis, and balance sheet auditing.\n"
                    "3. **Corporate Finance & Valuation:** Capital budgeting, working capital optimization, and mergers & acquisitions concepts.\n"
                    "4. **Financial Software:** Proficiency in ERP systems (SAP, Tally), Bloomberg Terminal, or Power BI for financial dashboards.\n"
                    "5. **Regulatory Compliance:** Tax laws, securities regulations, and ethical risk management standards (SDG 8).\n\n"
                    "**Next step:** Are you interested in Corporate Finance, Investment Banking, or Chartered Accountancy (CA)?"
                )
            elif "gov" in norm_c or "upsc" in norm_c or "civil services" in norm_c:
                return (
                    "### 🏛️ Essential Skills for Government & Public Sector Jobs\n\n"
                    "Preparing for competitive government exams (UPSC, SSC, State PSC, Banking) requires structured multi-disciplinary competencies:\n\n"
                    "1. **General Studies & Current Affairs:** Comprehensive knowledge of History, Polity, Geography, Economy, and International Relations.\n"
                    "2. **Quantitative Aptitude & Reasoning:** Speed and accuracy in numerical problem-solving, data interpretation, and logical puzzles.\n"
                    "3. **Descriptive & Essay Writing:** Articulating structured, balanced policy viewpoints with evidence and clarity.\n"
                    "4. **Public Administration Awareness:** Understanding government machinery, constitutional provisions, and public grievance mechanisms.\n"
                    "5. **Exam Strategy & Mental Resilience:** Time management under pressure and consistent answer-writing practice.\n\n"
                    "**Next step:** Which specific government examination (UPSC, SSC, Banking, or State PSC) are you aiming for?"
                )
            elif "pharm" in norm_c:
                return (
                    "### 💊 Essential Skills for Pharmacy & Pharmaceutical Sciences\n\n"
                    "To build a strong, employable profile in **Pharmacy**, focus on these core scientific, clinical, and regulatory capabilities:\n\n"
                    "1. **Pharmacology & Therapeutics:** Deep understanding of drug mechanisms of action, pharmacokinetics (ADME), dosage calculations, and drug-drug interactions.\n"
                    "2. **Pharmaceutics & Formulation:** Compounding, sterile preparation techniques, dosage form design (tablets, injectables, ointments), and stability testing.\n"
                    "3. **Pharmaceutical Analysis & Lab Skills:** Operating laboratory analytical equipment such as HPLC, UV-Vis spectrophotometry, dissolution apparatus, and titration.\n"
                    "4. **Clinical Patient Counseling:** Clear communication on medication adherence, administration guidelines, contraindications, and managing adverse drug events.\n"
                    "5. **Regulatory Affairs & Quality Standards:** Good Manufacturing Practices (GMP), Good Laboratory Practices (GLP), pharmacovigilance reporting, and drug licensing regulations (SDG 8).\n\n"
                    "**Next step:** Are you interested in Community/Hospital Pharmacy, Industrial R&D/Formulation, or Regulatory Affairs?"
                )
            elif any(k in norm_c for k in ["btech cse", "cse", "computer science"]):
                return (
                    "### 💻 Essential Skills for B.Tech Computer Science & Engineering (CSE)\n\n"
                    "To build a competitive, high-demand profile in **B.Tech CSE**, focus on these core foundational, algorithmic, and engineering competencies:\n\n"
                    "1. **Data Structures & Algorithms (DSA):** Arrays, Strings, Linked Lists, Stacks/Queues, Trees, Graphs, and Dynamic Programming in C++, Java, or Python.\n"
                    "2. **Core CS Theory & Systems:** Operating Systems (process scheduling, memory virtualization), Database Management Systems (SQL, normalization, indexing), and Computer Networks (TCP/IP, HTTP, routing).\n"
                    "3. **Applied Technical Track:**\n"
                    "   • *Full-Stack Development:* Modern frontend (React/Next.js), backend APIs (FastAPI/Node.js/Spring Boot), and databases (PostgreSQL/MongoDB).\n"
                    "   • *Cloud & DevOps:* Docker containerization, Kubernetes orchestration, CI/CD pipelines, and cloud platforms (AWS/GCP).\n"
                    "   • *AI/ML & Data Engineering:* Data processing with Pandas/NumPy, machine learning with Scikit-Learn/PyTorch, and scalable ETL pipelines.\n"
                    "   • *Cybersecurity:* Cryptographic protocols, secure coding standards (OWASP), and network security.\n"
                    "4. **Developer Tooling:** Git & GitHub version control, Linux command line, Postman for API testing, and automated testing frameworks.\n"
                    "5. **Workplace & Employability Skills:** Clean code architecture, documentation, problem decomposition, and ethical software practices (SDG 8).\n\n"
                    "**Next step:** Which technical track (Software Engineering/SDE, AI/ML, Cloud/DevOps, or Cybersecurity) are you most interested in pursuing?"
                )

        # General response when no career has been specified yet:
        return (
            "### 🎯 How to Decide What Skills to Learn\n\n"
            "Because every career path requires different technical tools, the skills you should prioritize depend directly "
            "on your **target profession**:\n\n"
            "#### 1. Universal Workplace Skills (Valuable in Every Field)\n"
            "• **Communication & Articulation:** Written documentation and interpersonal presentation.\n"
            "• **Problem-Solving & Critical Thinking:** Analyzing root causes and making data-informed decisions.\n"
            "• **Digital Competence:** Everyday productivity tools, spreadsheets (Excel), and digital collaboration platforms.\n\n"
            "#### 2. Domain-Specific Technical Skills (Examples by Profession)\n"
            "• **Civil Engineering:** AutoCAD, STAAD Pro, Surveying, Structural Analysis.\n"
            "• **Mechanical Engineering:** SolidWorks, Thermodynamics, ANSYS, CNC manufacturing.\n"
            "• **Medicine & Healthcare:** Clinical diagnosis, pharmacology, anatomy, patient triage.\n"
            "• **Law:** Legal drafting, case law research (SCC/Manupatra), moot court advocacy.\n"
            "• **Teaching:** Pedagogy, lesson planning, classroom management, student assessment.\n"
            "• **Design:** Figma, Photoshop, Illustrator, typography, branding portfolio.\n"
            "• **Finance:** Financial modeling, corporate accounting, valuation, Excel.\n"
            "• **Software / Tech:** Programming (Python/Java), Data Structures, Databases, Web APIs.\n\n"
            "**Next step:** What career, profession, or subject area interests you most? Tell me, and I will generate your exact skill roadmap!"
        )

    # 4. Handling Internships across diverse careers
    if "internship" in lower and ("what" in lower or "where" in lower or "how" in lower or "should i do" in lower or "guidance" in lower):
        norm_c = active_career.lower()
        if "civil" in norm_c or "civil" in lower:
            return (
                "### 🏗️ Recommended Internships for Civil Engineering\n\n"
                "In Civil Engineering, practical site exposure is the single most valuable asset for employability:\n\n"
                "1. **Construction Site Supervision:** Work with construction firms, contractors, or builders on active residential/commercial sites to observe concrete pouring, rebar placement, and quality checks.\n"
                "2. **Structural Design Consultancies:** Intern with design firms to work under licensed structural engineers using AutoCAD, STAAD Pro, or ETABS.\n"
                "3. **Infrastructure & Highway Projects:** Apply for internships with public works departments, metro rail projects, or highway authorities (e.g. NHAI / PWD / L&T / Shapoorji).\n"
                "4. **Geotechnical & Surveying Labs:** Gain experience in soil testing laboratories and field surveying using Total Stations.\n\n"
                "**SDG 8 Connection:** On-site safety protocols and verified fieldwork prepare you for safe, productive professional employment.\n\n"
                "**Next step:** Have you completed foundational coursework in Structural Analysis and AutoCAD?"
            )
        elif "mech" in norm_c or "mechanical" in lower:
            return (
                "### ⚙️ Recommended Internships for Mechanical Engineering\n\n"
                "Mechanical Engineering employers value hands-on shop-floor and design-office experience:\n\n"
                "1. **Automotive & Heavy Industry:** Production and assembly line internships at automotive OEMs, tier-1 suppliers, or heavy machinery manufacturers.\n"
                "2. **CAD/CAM & Product Design Firms:** Assist design teams in 3D part modeling, drafting, and tolerance stack-up analysis using SolidWorks or CATIA.\n"
                "3. **Thermal & Energy Plants:** Summer training at power generation plants, HVAC installation companies, or refinery facilities.\n"
                "4. **CNC Machining & Tool Rooms:** Hands-on training in precision manufacturing, tool rooms (MSME tool rooms), and quality assurance.\n\n"
                "**Next step:** Do you prefer hands-on manufacturing/maintenance or CAD design and simulation?"
            )
        elif "doctor" in norm_c or "medicine" in norm_c or "medical" in lower:
            return (
                "### 🩺 Clinical Postings & Rotatory Internship in Medicine\n\n"
                "In Medicine, clinical training is integrated directly into formal qualifications:\n\n"
                "1. **Compulsory Rotatory Housemanship / Medical Internship:** 12 months of structured rotations across General Medicine, Surgery, Pediatrics, Obstetrics & Gynecology, Orthopedics, and Community Health.\n"
                "2. **Clinical Observerships:** Shadowing attending physicians and consultants in specialized tertiary hospital departments during undergraduate years.\n"
                "3. **Community Health Camps:** Participating in rural health centers, vaccination drives, and primary healthcare clinics to understand public health realities (SDG 8).\n\n"
                "**Next step:** Are you seeking advice on licensing examination preparation or specialty rotation planning?"
            )
        elif "law" in norm_c or "lawyer" in lower:
            return (
                "### ⚖️ Recommended Internships for Law Students\n\n"
                "Building a strong legal resume requires diverse exposure across the legal ecosystem:\n\n"
                "1. **Trial Court / District Court Advocates:** Learn fundamental litigation procedure, client interviewing, and courtroom filing basics.\n"
                "2. **High Court & Supreme Court Chambers:** Observe appellate advocacy, writ petitions, and deep constitutional arguments.\n"
                "3. **Corporate Law Firms:** Intern in corporate transactional departments assisting with due diligence, contract review, and M&A documentation.\n"
                "4. **Legal Aid & Human Rights NGOs:** Provide free legal assistance to underprivileged citizens, advancing SDG 8 and SDG 16 principles.\n\n"
                "**Next step:** Do you intend to practice dispute litigation in the courts or work in corporate advisory?"
            )
        elif "design" in norm_c or "graphic" in lower:
            return (
                "### 🎨 Recommended Internships for Graphic Designers\n\n"
                "Design internships should provide real portfolio pieces and client collaboration experience:\n\n"
                "1. **Branding & Creative Agencies:** Work on client identities, brand style guides, marketing collateral, and packaging.\n"
                "2. **Tech Startups & Product Teams:** Support UI/UX teams by designing visual assets, social graphics, and interface components in Figma.\n"
                "3. **Publishing & Media Houses:** Editorial layout design for digital publications, magazines, and marketing campaigns.\n\n"
                "**Next step:** Do you have a live portfolio link (e.g. Behance, Dribbble, or personal site) ready for applications?"
            )
        elif "finance" in norm_c:
            return (
                "### 💼 Recommended Internships for Finance & Accounting\n\n"
                "Finance internships demonstrate numerical rigor and commercial awareness:\n\n"
                "1. **Commercial & Retail Banking:** Credit appraisal, retail loan operations, and customer wealth management.\n"
                "2. **Chartered Accountancy & Audit Firms:** Articleship or internships in statutory audit, tax computation, and compliance.\n"
                "3. **Corporate Finance Teams:** Financial planning and analysis (FP&A), cash flow budgeting, and variance analysis in operating companies.\n\n"
                "**Next step:** Are you targeting auditing/accounting, commercial banking, or equity research?"
            )
        elif "pharm" in norm_c or "pharmacy" in lower or "pharmacist" in lower:
            return (
                "### 💊 Recommended Internships for Pharmacy Students\n\n"
                "Pharmacy education requires practical training across healthcare and industrial settings to build professional competence:\n\n"
                "1. **Hospital Pharmacy Internships:** Gain experience in inpatient and outpatient hospital pharmacies, drug distribution, inpatient chart review, and sterile IV compounding.\n"
                "2. **Community / Retail Pharmacy Practice:** Learn prescription verification, inventory management, patient counseling, and point-of-care health screenings under a licensed pharmacist.\n"
                "3. **Pharmaceutical Manufacturing & QC/QA:** Industrial internships in pharmaceutical formulation plants, quality control labs (HPLC/spectroscopy), and packaging compliance.\n"
                "4. **Clinical Research & Pharmacovigilance Organizations (CROs):** Internships in clinical trials data monitoring, adverse event reporting, and drug regulatory documentation.\n\n"
                "**SDG 8 Connection:** Adhering to good dispensing practices and patient safety standards ensures high-quality, ethical healthcare delivery.\n\n"
                "**Next step:** Do you plan to pursue hospital clinical practice, retail pharmacy, or the pharmaceutical manufacturing industry?"
            )
        elif any(k in norm_c for k in ["btech cse", "cse", "computer science"]) or any(k in lower for k in ["btech cse", "cse", "computer science"]):
            return (
                "### 💻 Recommended Internships for B.Tech CSE Students\n\n"
                "In Computer Science & Engineering, hands-on production code, collaborative Git workflows, and verifiable projects are critical for placement success:\n\n"
                "1. **Software Development Engineer (SDE) Internships:** Work with product tech startups, mid-sized firms, or enterprise tech teams developing REST APIs, database schemas, and frontend features.\n"
                "2. **Open-Source Fellowship Programs:** Participate in Google Summer of Code (GSoC), MLH Fellowship, LFX Mentorship, or contribute to major GitHub open-source repositories.\n"
                "3. **Research & Academic Internships:** Apply for summer research fellowships at IITs, NITs, IIITs, or international universities focusing on AI/ML, systems engineering, distributed computing, or cybersecurity.\n"
                "4. **Cloud & DevOps Internships:** Gain experience in containerization (Docker), deployment automation, Kubernetes, and cloud infrastructure monitoring.\n"
                "5. **Data & Analytics Internships:** Work on real-world data pipelines, SQL querying, dashboard development, or machine learning model evaluation.\n\n"
                "**SDG 8 Connection:** Developing productive digital skills drives technological innovation, digital inclusion, and quality employment.\n\n"
                "**Next step:** Do you already have a GitHub profile with 1–2 deployed personal projects?"
            )
        else:
            field_str = active_career.title() if active_career else "your chosen profession"
            return (
                f"### 💼 Internship Strategy for {field_str}\n\n"
                f"Securing practical internship exposure in **{field_str}** significantly enhances your employability:\n\n"
                f"1. **Identify Target Sectors:** Look for established firms, research centers, clinics, or studios in {field_str}.\n"
                f"2. **Prepare Portfolio / Sample Work:** Showcase tangible projects, technical coursework, or certifications on your resume.\n"
                f"3. **Direct Networking:** Connect with practitioners and alumni on LinkedIn who are currently working in {field_str}.\n"
                f"4. **Verified Learning & Safety:** Prioritize internships that offer structured mentorship and adhere to fair workplace standards (SDG 8).\n\n"
                f"**Next step:** What type of organizations or companies in {field_str} are you most interested in interning with?"
            )

    # 5. Dedicated Career Roadmaps & Inquiries
    # Civil Engineering
    if "civil engineer" in lower or ("civil" in lower and any(w in lower for w in ["roadmap", "banna hai", "become", "career"])):
        return (
            "### 🏗️ Complete Career Roadmap: Civil Engineering\n\n"
            "Civil Engineering is a foundational pillar of sustainable infrastructure and economic growth (SDG 8). "
            "Here is the comprehensive step-by-step career path:\n\n"
            "#### Stage 1: Educational Foundation\n"
            "• **10+2 / High School:** Physics, Chemistry, and Mathematics (PCM).\n"
            "• **Degree Program:** B.Tech / B.E. / B.S. in Civil Engineering (4 years) or Diploma in Civil Engineering (3 years).\n"
            "• **Core Subjects:** Engineering Mechanics, Strength of Materials, Fluid Mechanics, Surveying, Concrete Technology.\n\n"
            "#### Stage 2: Core Domain Skills & Software\n"
            "• **Drafting & Modeling:** Master **AutoCAD** for 2D engineering drawings and **Autodesk Revit** for Building Information Modeling (BIM).\n"
            "• **Structural Analysis:** Learn **STAAD Pro**, **ETABS**, or **SAP2000** for structural design and load calculations.\n"
            "• **Field Surveying:** Hands-on competence with Total Station, leveling instruments, and GPS.\n\n"
            "#### Stage 3: Practical Site Exposure & Internships\n"
            "• On-site internships with construction contractors or infrastructure builders (residential, highways, bridges).\n"
            "• Familiarity with soil testing, concrete slump tests, rebar inspection, and quantity surveying.\n"
            "• Understand Occupational Safety and Health standards on construction sites (SDG 8).\n\n"
            "#### Stage 4: Professional Specialization & Licensing\n"
            "• Choose a track: *Structural, Geotechnical, Transportation, Environmental, or Construction Project Management*.\n"
            "• Licensing / Certifications: Professional Engineer (PE) license / Chartership, project management certifications (PMP/CAPM).\n\n"
            "#### Stage 5: Career Opportunities\n"
            "• Roles: Site Engineer, Structural Design Engineer, Quality Control Engineer, Quantity Surveyor, Project Manager.\n"
            "• Sectors: Infrastructure developers (L&T, Shapoorji, Tata Projects), public works departments, consultancy firms, international engineering agencies.\n\n"
            "**Next step:** What stage of your education are you currently in (school, college, or graduate)?"
        )

    # Mechanical Engineering
    if "mechanical engineer" in lower or ("mechanical" in lower and any(w in lower for w in ["roadmap", "banna hai", "banva", "become", "career"])):
        return (
            "### ⚙️ Complete Career Roadmap: Mechanical Engineering\n\n"
            "Mechanical Engineering powers industrial innovation, manufacturing efficiency, and clean energy systems under SDG 8:\n\n"
            "#### Stage 1: Academic Foundations\n"
            "• **10+2 / High School:** Physics, Chemistry, and Mathematics (PCM).\n"
            "• **Degree:** B.Tech / B.E. in Mechanical Engineering (4 years) or Diploma in Mechanical Engineering.\n"
            "• **Fundamental Topics:** Engineering Mechanics, Strength of Materials, Thermodynamics, Fluid Mechanics, Theory of Machines.\n\n"
            "#### Stage 2: CAD, Simulation & Modern Manufacturing\n"
            "• **3D CAD Software:** Master **SolidWorks**, **CATIA**, or **PTC Creo** for mechanical design and drafting.\n"
            "• **Engineering Simulation (FEA & CFD):** Learn **ANSYS** for structural stress and thermal/fluid flow analysis.\n"
            "• **Manufacturing Technology:** CNC programming, GD&T, 3D printing, and automated assembly.\n\n"
            "#### Stage 3: Industrial Experience & Projects\n"
            "• Hands-on capstone project: Design a functional mechanical system, gear train, robotic arm, or thermal exchanger.\n"
            "• Industrial internships in automotive plants, manufacturing units, or engineering design consultancies.\n"
            "• Understand industrial safety standards, lean manufacturing (5S, Kaizen), and sustainable production (SDG 8).\n\n"
            "#### Stage 4: Entry Roles & Career Growth\n"
            "• Entry Roles: Mechanical Design Engineer, Production/Manufacturing Engineer, Quality Assurance Engineer, HVAC Engineer.\n"
            "• Long-Term: Lead Systems Engineer, Plant Manager, R&D Specialist, or Engineering Consultant.\n\n"
            "**Next step:** Are you more drawn toward Product Design & CAD, or Manufacturing & Plant Operations?"
        )

    # B.Tech CSE / Computer Science Engineering
    if any(w in lower for w in ["btech cse", "b.tech cse", "computer science engineering", "cse", "computer science"]) and (
        any(w in lower for w in ["roadmap", "banna", "become", "career", "study", "guidance", "explain", "pathway", "path", "how to", "plan", "4 year", "4-year"]) or
        lower.strip() in ["btech cse", "b.tech cse", "cse", "computer science"]
    ):
        return (
            "### 💻 Complete 4-Year Career Roadmap: B.Tech Computer Science & Engineering (CSE)\n\n"
            "B.Tech CSE is a premier engineering discipline powering software development, scalable system architecture, and economic innovation under UN SDG 8:\n\n"
            "#### Year 1: Computational Foundations & First Language\n"
            "• **Core Subjects:** Engineering Mathematics (Calculus, Linear Algebra, Discrete Math), Basics of Electrical/Electronics, Engineering Physics.\n"
            "• **Programming Foundations:** Master your first language deeply (**C++** or **Java** for DSA, or **Python** for rapid prototyping).\n"
            "• **Developer Tools:** Learn **Git & GitHub** for version control, basic Linux terminal navigation, and Markdown documentation.\n"
            "• **Milestone:** Build foundational logic, solve 50+ basic algorithmic problems, and build a simple CLI application.\n\n"
            "#### Year 2: Data Structures, Algorithms & Core Systems\n"
            "• **Core Subjects:** Data Structures & Algorithms (**DSA**), Object-Oriented Programming (**OOP**), Computer Organization & Architecture (COA).\n"
            "• **Problem Solving:** Consistently solve problems on LeetCode / HackerRank (Arrays, Linked Lists, Stacks, Queues, Binary Trees, Recursion).\n"
            "• **Specialization Track Selection:** Choose an applied path (Full-Stack Web Dev, Cloud/DevOps, AI/ML, or Mobile App Development).\n"
            "• **Milestone:** Build and deploy a complete project with database persistence (e.g. REST API, CRUD web app, or full-stack portal).\n\n"
            "#### Year 3: Advanced Systems, Capstone & Internships\n"
            "• **Core Subjects:** Operating Systems (**OS**), Database Management Systems (**DBMS** & SQL), Computer Networks (**CN**), Theory of Computation (TOC).\n"
            "• **Advanced DSA & LLD:** Graphs, Dynamic Programming, Tries, and Low-Level Object-Oriented System Design (LLD).\n"
            "• **Production Project:** Deploy a robust full-stack application with authentication, API rate-limiting, and cloud hosting (AWS/Vercel/Render).\n"
            "• **Internships:** Apply for summer SDE internships, open-source programs (GSoC, MLH), and corporate hackathons.\n"
            "• **Milestone:** Complete a verified summer tech internship and solve 200+ quality DSA problems.\n\n"
            "#### Year 4: High-Level Design, Placements & Launch\n"
            "• **Electives:** Cloud Computing, Distributed Systems, Machine Learning, Compiler Design, Information Security.\n"
            "• **Placement Preparation:** System Design (HLD/LLD), mock technical coding interviews, core CS fundamentals revision, and behavioral STAR rounds.\n"
            "• **Final Year Capstone:** A major engineering project addressing real-world challenges, accessibility, or social impact (SDG 8).\n"
            "• **Career Roles:** Software Development Engineer (SDE-1), Backend Developer, Frontend Engineer, Cloud/DevOps Engineer, Data Engineer, Cybersecurity Analyst.\n\n"
            "**Next step:** Which year of B.Tech CSE are you in (1st, 2nd, 3rd, or 4th year), and what technical track interests you most?"
        )

    # Pharmacy / Pharmacist
    if any(w in lower for w in ["pharmacy", "pharmacist"]) and any(w in lower for w in ["roadmap", "banna", "become", "career", "study", "guidance", "explain", "pathway", "path", "how to"]):
        return (
            "### 💊 Complete Career Roadmap: Pharmacy & Pharmaceutical Sciences\n\n"
            "Pharmacy is a vital healthcare and life-sciences profession dedicated to the discovery, formulation, clinical dispensing, and safe monitoring of medications (SDG 8 & SDG 3):\n\n"
            "#### Stage 1: Educational Pathways & Degree Options\n"
            "• **10+2 / High School Foundation:** Physics, Chemistry, and Biology (PCB) or Mathematics (PCM) with strong standing in chemical sciences.\n"
            "• **Undergraduate Degree Routes:**\n"
            "  • **D.Pharm (Diploma in Pharmacy - 2 Years):** Foundational credential qualifying for community chemist licensing and retail pharmacy dispensing.\n"
            "  • **B.Pharm (Bachelor of Pharmacy - 4 Years):** Industry-standard degree covering drug formulation, pharmaceutical analysis, medicinal chemistry, and quality control.\n"
            "  • **Pharm.D (Doctor of Pharmacy - 6 Years):** Clinical doctorate program focused on hospital ward rounds, clinical pharmacokinetics, therapeutic drug monitoring, and direct patient care.\n\n"
            "#### Stage 2: Core Subjects & Laboratory Competencies\n"
            "• **Pharmacology & Toxicology:** Mechanisms of drug action, receptor pathways, organ systems, and contraindications.\n"
            "• **Pharmaceutics & Formulation:** Compounding, tablet compression, injectables, ointments, suspensions, and bio-availability.\n"
            "• **Medicinal Chemistry & Pharmacognosy:** Chemical structure of active pharmaceutical ingredients (APIs) and plant-derived phytomedicines.\n"
            "• **Instrumental Laboratory Analysis:** Hands-on proficiency with HPLC, UV-Vis spectrophotometry, dissolution testing, and Karl Fischer titration.\n\n"
            "#### Stage 3: Practical Training, Lab Skills & Internships\n"
            "• Mandatory 500+ hours of hospital and community pharmacy practice as prescribed by statutory pharmacy councils.\n"
            "• Industrial training in pharmaceutical manufacturing units: Current Good Manufacturing Practices (cGMP), cleanroom protocols, and validation.\n"
            "• Soft skills: Empathetic patient counseling, prescription auditing, and inter-professional communication with healthcare teams.\n\n"
            "#### Stage 4: Professional Licensing & Registration\n"
            "• Register with the State or National Pharmacy Council to receive your official **Registered Pharmacist (R.Ph)** license and dispensing rights.\n\n"
            "#### Stage 5: Career Opportunities & Specializations\n"
            "• **Hospital & Clinical Pharmacy:** Hospital Pharmacist, Clinical Specialist, Medication Safety Coordinator.\n"
            "• **Pharmaceutical Industry:** Formulation R&D Scientist, Quality Assurance (QA) / Quality Control (QC) Officer, Production Executive.\n"
            "• **Regulatory Affairs & Pharmacovigilance:** Drug Safety Associate, Regulatory Dossier Specialist (eCTD filings for US FDA/EMA), Clinical Research Associate (CRA).\n"
            "• **Retail & Entrepreneurship:** Community Pharmacist, Pharmacy Chain Manager, Independent Pharmacy Owner.\n"
            "• **Postgraduate & Research:** M.Pharm, Ph.D., MBA in Pharmaceutical Management.\n\n"
            "**Next step:** Are you interested in Hospital/Clinical Pharmacy, Pharmaceutical Industry/R&D, or Retail Pharmacy?"
        )

    # Medicine / Doctor
    if any(w in lower for w in ["doctor", "mbbs", "medicine", "physician"]) and any(w in lower for w in ["after 12th", "become", "career", "roadmap", "study", "banna"]):
        return (
            "### 🩺 Career Pathway to Becoming a Doctor (Medicine)\n\n"
            "A career in medicine requires deep dedication, rigorous clinical training, and a lifelong commitment to ethical patient care (SDG 8):\n\n"
            "#### 1. High School Foundation (10+2)\n"
            "• **Subjects:** Physics, Chemistry, and Biology (PCB) with strong academic standing.\n"
            "• **Entrance Examination:** Competitive national pre-medical test (e.g. **NEET-UG** in India, **MCAT** in the US/Canada, **UCAT/BMAT** in the UK).\n\n"
            "#### 2. Undergraduate Medical Education (MBBS / MD)\n"
            "• **Duration:** ~5.5 years (typically 4.5 years of academic study + 1 year compulsory rotatory internship).\n"
            "• **Phases:**\n"
            "  • *Pre-Clinical:* Anatomy, Physiology, Biochemistry.\n"
            "  • *Para-Clinical:* Pathology, Microbiology, Pharmacology, Forensic Medicine.\n"
            "  • *Clinical:* General Medicine, General Surgery, Pediatrics, Obstetrics & Gynecology, Orthopedics, Ophthalmology, Community Medicine.\n\n"
            "#### 3. Compulsory Rotatory Internship\n"
            "• Hands-on clinical postings across emergency, surgery, wards, outpatient clinics, and rural health centers under senior medical faculty supervision.\n\n"
            "#### 4. Licensing & Council Registration\n"
            "• Register with the National/State Medical Council to earn the official license to practice medicine independently.\n\n"
            "#### 5. Post-Graduate Specialization (MD / MS / DNB)\n"
            "• Additional 3 years of residency training to become a specialist (e.g. Cardiologist, Orthopedic Surgeon, Pediatrician, Neurologist).\n\n"
            "**Next step:** Are you currently in school preparing for medical entrance exams, or seeking guidance on medical college life?"
        )

    # Law / Lawyer
    if any(w in lower for w in ["lawyer", "advocate", "law"]) and any(w in lower for w in ["become", "career", "roadmap", "banna", "study", "guidance"]):
        return (
            "### ⚖️ Career Pathway to Becoming a Lawyer\n\n"
            "The legal profession upholds justice, human rights, and the rule of law—vital foundations for sustainable economic growth (SDG 8 & SDG 16):\n\n"
            "#### 1. Educational Routes\n"
            "• **Route A (After 12th):** 5-year integrated law degree (BA LLB, BBA LLB, or B.Sc LLB) via entrance tests like **CLAT**, AILET, or LSAT.\n"
            "• **Route B (After Graduation):** 3-year LLB degree after completing an undergraduate bachelor's degree in any discipline.\n\n"
            "#### 2. Core Curriculum & Law School Activities\n"
            "• **Core Subjects:** Constitutional Law, Criminal Law (IPC/CrPC), Civil Procedure, Contract Law, Torts, Property Law, Corporate Law.\n"
            "• **Practical Experience:** Active participation in **Moot Court Competitions**, Legal Aid Clinics, and Model United Nations (MUN).\n\n"
            "#### 3. Internships During Law School\n"
            "• Progressive internships: Trial Court Advocates $\\rightarrow$ High Court / Supreme Court Senior Chambers $\\rightarrow$ Corporate Law Firms or NGOs.\n\n"
            "#### 4. Bar Licensing & Enrollment\n"
            "• Enroll with the State Bar Council and pass the **Bar Examination** (e.g. All India Bar Examination - AIBE) to receive the Certificate of Practice.\n\n"
            "#### 5. Career Specializations\n"
            "• **Litigation:** Practicing in trial courts, appellate tribunals, High Courts, and Supreme Court.\n"
            "• **Corporate Law:** Transactional advisory, mergers & acquisitions, contract management, and compliance.\n"
            "• **Judicial Services:** Taking State Judicial Services Examination to become a Civil Judge / Magistrate.\n\n"
            "**Next step:** Do you see yourself arguing cases in courtrooms or working as a corporate legal advisor?"
        )

    # Teacher / Teaching
    if any(w in lower for w in ["teacher", "teaching", "educator", "professor"]) and any(w in lower for w in ["become", "career", "roadmap", "banna", "guidance"]):
        return (
            "### 📚 Career Pathway to Becoming a Teacher / Educator\n\n"
            "Teaching is one of the most respected professions, empowering future generations and fostering decent work (SDG 4 & SDG 8):\n\n"
            "#### 1. Educational Qualifications by Level\n"
            "• **Primary School Teacher (Grades 1–5):** 10+2 followed by a Diploma in Elementary Education (D.El.Ed) + Primary Teacher Eligibility Test (TET).\n"
            "• **Trained Graduate Teacher - TGT (Grades 6–10):** Bachelor's degree in your chosen subject (BA/B.Sc) + Bachelor of Education (**B.Ed**) + State/Central TET.\n"
            "• **Post Graduate Teacher - PGT (Grades 11–12):** Master's degree in your subject (MA/M.Sc/M.Com) + B.Ed degree.\n"
            "• **College / University Professor:** Master's degree (55%+) + Qualifying the **NET** (National Eligibility Test) or **SET**, and preferably a Ph.D.\n\n"
            "#### 2. Pedagogical Skills & Practical Training\n"
            "• Complete student-teaching internships in real schools during your B.Ed program.\n"
            "• Master lesson planning, inclusive classroom management, child psychology, and educational evaluation.\n\n"
            "#### 3. Modern Educational Tools\n"
            "• Familiarity with smart boards, learning management systems (Google Classroom, Canvas), and interactive digital teaching tools.\n\n"
            "**Next step:** What subject and age group (primary school, secondary school, or college/university) do you wish to teach?"
        )

    # Graphic Design
    if any(w in lower for w in ["graphic design", "graphic designer", "ui/ux designer"]) and any(w in lower for w in ["become", "career", "roadmap", "banna", "guidance"]):
        return (
            "### 🎨 Complete Career Roadmap: Graphic Design\n\n"
            "Graphic design combines visual storytelling, artistic principles, and digital communication to build compelling brand identities:\n\n"
            "#### Stage 1: Design Fundamentals (Theory)\n"
            "• **Core Principles:** Visual hierarchy, alignment, balance, white space, and contrast.\n"
            "• **Typography:** Font anatomy, pairing serifs and sans-serifs, kerning, and legibility.\n"
            "• **Color Theory:** Color psychology, color harmonies, RGB vs CMYK, and accessibility.\n\n"
            "#### Stage 2: Industry-Standard Software\n"
            "• **Adobe Illustrator:** Vector design, logos, icons, illustrations, and brand assets.\n"
            "• **Adobe Photoshop:** Image manipulation, retouching, visual mockups, and digital compositions.\n"
            "• **Figma:** Digital interface layouts, wireframing, UI/UX prototyping, and web assets.\n"
            "• **Adobe InDesign:** Multi-page editorial layouts, brochures, books, and PDF publications.\n\n"
            "#### Stage 3: Portfolio Development (Most Crucial!)\n"
            "• Create 3–5 comprehensive, realistic case studies (e.g. complete brand identity, packaging design, app redesign).\n"
            "• Publish and document your creative process on **Behance** or **Dribbble** with high-resolution mockups.\n\n"
            "#### Stage 4: Internships & Freelance Experience\n"
            "• Intern with design studios, advertising agencies, or tech startups.\n"
            "• Take small freelance projects to learn client communication, invoicing, and deadline management.\n\n"
            "**Next step:** Have you started learning any design tools like Figma, Illustrator, or Photoshop yet?"
        )

    # Finance
    if any(w in lower for w in ["finance", "banking", "accountant", "chartered accountant"]) and any(w in lower for w in ["work in", "career", "roadmap", "become", "field", "guidance"]):
        return (
            "### 💼 Complete Career Roadmap: Finance & Banking\n\n"
            "A career in finance drives capital allocation, economic productivity, and strategic decision-making (SDG 8):\n\n"
            "#### Stage 1: Academic Foundation\n"
            "• **Undergraduate Degree:** Bachelor's in Commerce (B.Com), Economics, Finance (BFIA/BAF), or Business Administration (BBA).\n"
            "• **Core Knowledge:** Financial Accounting, Managerial Accounting, Micro/Macroeconomics, Business Statistics, Corporate Law.\n\n"
            "#### Stage 2: Technical & Modeling Tools\n"
            "• **Advanced Microsoft Excel:** Lookup functions, pivot tables, scenario analysis, and macro automation.\n"
            "• **Financial Modeling & Valuation:** Building 3-statement models, DCF valuation, and comparable company analysis.\n"
            "• **Accounting & BI Software:** ERP systems (SAP, Tally), Power BI, or Tableau for financial visualization.\n\n"
            "#### Stage 3: Professional Certifications (High Industry Value)\n"
            "• **Chartered Accountancy (CA / CPA):** Gold standard for auditing, taxation, and financial compliance.\n"
            "• **Chartered Financial Analyst (CFA):** Premier global certification for investment management, portfolio strategy, and equity research.\n"
            "• **Financial Risk Manager (FRM):** Specialized in credit, market, and operational risk.\n"
            "• **MBA in Finance:** Tier-1 business school degree for investment banking and corporate strategy.\n\n"
            "#### Stage 4: Career Pathways\n"
            "• Roles: Financial Analyst, Investment Banking Analyst, Corporate Treasurer, Risk Manager, Equity Research Associate, Auditor.\n\n"
            "**Next step:** Which direction in finance (Corporate Finance, Investment Banking, Auditing, or Commercial Banking) interests you most?"
        )

    # Government Jobs
    if any(w in lower for w in ["government job", "government jobs", "civil services", "upsc", "ssc", "sarkari"]) and any(w in lower for w in ["prepare", "career", "roadmap", "guidance", "how to"]):
        return (
            "### 🏛️ Complete Preparation Roadmap: Government & Civil Services\n\n"
            "Public sector careers offer meaningful avenues to contribute to public welfare, policy enforcement, and inclusive national development (SDG 8):\n\n"
            "#### 1. Identify Your Target Examination\n"
            "• **UPSC Civil Services (IAS, IPS, IFS, IRS):** Premier administrative and policy leadership positions.\n"
            "• **Staff Selection Commission (SSC CGL / CHSL):** Officers, inspectors, and staff in central ministries and departments.\n"
            "• **Banking Examinations (IBPS PO, SBI PO, RBI Grade B):** Officers in public sector banks and central regulatory authority.\n"
            "• **State Public Service Commissions (State PSC):** Administrative officers in state governance.\n"
            "• **Defence Services (NDA, CDS, AFCAT):** Commissioned officers in Armed Forces.\n\n"
            "#### 2. Eligibility & Educational Foundation\n"
            "• A recognized Bachelor's degree in any discipline (B.A, B.Sc, B.Com, B.Tech, etc.) satisfies eligibility for almost all major exams.\n\n"
            "#### 3. Core Pillars of Preparation\n"
            "• **General Studies:** Indian Polity, Economy, Modern History, Geography, Environment, and General Science.\n"
            "• **Current Affairs:** Consistent daily study of reputed national newspapers (e.g. The Hindu or Indian Express) and monthly compilations.\n"
            "• **Quantitative Aptitude & Logical Reasoning:** Regular practice of mathematical shortcuts, data interpretation, and deductive logic.\n"
            "• **Language & Essay Writing:** Building clear, balanced, and evidence-based descriptive writing skills.\n\n"
            "#### 4. Rigorous Practice & Testing\n"
            "• Solve the last 10 years of official previous year question papers (PYQs).\n"
            "• Enroll in regular test series to master time management and negative marking strategies.\n\n"
            "**Next step:** Which specific examination (UPSC, SSC, Banking, or State PSC) are you planning to prepare for?"
        )

    # Architecture
    if "architect" in lower or "architecture" in lower:
        return (
            "### 📐 Complete Career Roadmap: Architecture\n\n"
            "Architects design functional, safe, and sustainable built environments advancing SDG 8 and SDG 11 (Sustainable Cities):\n\n"
            "#### 1. High School & Entrance\n"
            "• **10+2:** Physics, Chemistry, and Mathematics (PCM).\n"
            "• **Entrance Exams:** **NATA** (National Aptitude Test in Architecture) or **JEE Main Paper 2** (B.Arch).\n\n"
            "#### 2. Professional Degree Program\n"
            "• 5-year Bachelor of Architecture (**B.Arch**) approved by the Council of Architecture.\n"
            "• Focus areas: Architectural Design Studio, Building Construction, Climatology, Structural Systems, History of Architecture.\n\n"
            "#### 3. Modern Design & BIM Tools\n"
            "• Master **AutoCAD** (2D drafting), **Autodesk Revit** (BIM), **Rhino / Grasshopper** (parametric design), and **SketchUp / V-Ray** (rendering).\n\n"
            "#### 4. Practical Training & Professional Registration\n"
            "• Complete mandatory practical training / internship semester at a registered architectural firm.\n"
            "• Register with the official Council of Architecture to obtain your license and seal to practice as a certified architect.\n\n"
            "**Next step:** Are you preparing for architecture entrance exams or currently studying in a B.Arch program?"
        )

    # 6. Fallback Roadmap for any explicitly stated career or general roadmap inquiry
    if any(w in lower for w in ["roadmap", "steps", "how do i become", "guide", "career pathway", "pathway"]) or (active_career and "plan" in lower):
        if active_career:
            return (
                f"### 🎯 Structured Career Roadmap: **{active_career.title()}**\n\n"
                f"Here is the recommended progression from foundational preparation to professional practice for **{active_career.title()}**:\n\n"
                f"#### Stage 1: Educational Qualification & Core Theory\n"
                f"• Acquire the standard degree, diploma, or vocational qualification required in your region for {active_career}.\n"
                f"• Master foundational concepts, regulatory frameworks, and professional ethics.\n\n"
                f"#### Stage 2: Technical Tools & Practical Skills\n"
                f"• Identify and master the top 2–3 software, equipment, or methodologies used by industry professionals in {active_career}.\n"
                f"• Combine domain-specific capabilities with universal employability skills (communication, problem-solving, collaboration).\n\n"
                f"#### Stage 3: Applied Projects & Field Exposure\n"
                f"• Undertake real-world projects, lab experiments, or field reports to prove your hands-on competence.\n"
                f"• Document your portfolio or repository to demonstrate practical application of theory.\n\n"
                f"#### Stage 4: Internships & Practical Experience\n"
                f"• Seek verified internships, apprenticeships, or shadowing opportunities with established practitioners.\n"
                f"• Learn workplace safety, regulatory compliance, and day-to-day workflow under professional supervision (SDG 8).\n\n"
                f"#### Stage 5: Licensing, Certification & Entry Roles\n"
                f"• Obtain mandatory professional licenses, board certifications, or industry-recognized credentials.\n"
                f"• Prepare an industry-aligned resume and rehearse situational/technical interview scenarios.\n\n"
                f"**Next step:** What is your current academic stage or experience level in {active_career}?"
            )
        else:
            return (
                "### 🎯 Structured Career Roadmap Framework\n\n"
                "A successful career roadmap aligns your education, practical skills, and internships to achieve decent, productive employment (SDG 8):\n\n"
                "#### The 5 Universal Roadmap Stages:\n"
                "1. **Stage 1 - Academic Foundation:** Selecting the accredited degree, diploma, or vocational credential required for your field.\n"
                "2. **Stage 2 - Domain Tools & Methodologies:** Mastering industry software, laboratory apparatus, or professional trade standards.\n"
                "3. **Stage 3 - Hands-on Projects & Fieldwork:** Demonstrating applied problem-solving through capstone projects or portfolios.\n"
                "4. **Stage 4 - Supervised Internships & Practicum:** Gaining real workplace experience and learning occupational safety.\n"
                "5. **Stage 5 - Licensure, ATS Resume & Job Readiness:** Earning statutory licenses/certifications and preparing for behavioral interviews.\n\n"
                "**Next step:** Which specific career or field would you like a detailed roadmap for? (e.g. Pharmacy, Civil Engineering, Law, Teaching, Design, etc.)"
            )

    # 7. Resume Review
    is_resume_query = ("resume" in lower or "cv" in lower)
    has_resume_keywords = (
        ("education" in lower or "b.tech" in lower or "degree" in lower) and
        ("skills" in lower or "projects" in lower or "experience" in lower) and
        ("cgpa" in lower or "gpa" in lower or "projects:" in lower or "skills:" in lower or len(text.split()) > 15)
    )
    last_asst = ""
    for h in reversed(history):
        if h.get("role") == "assistant":
            last_asst = h.get("content", "").lower()
            break
    was_prompted_for_resume = "resume" in last_asst and ("paste" in last_asst or "review" in last_asst)

    if is_resume_query or has_resume_keywords or was_prompted_for_resume:
        is_asking_how = any(q in lower for q in ["how to", "help me", "how can i", "how do i", "tips for"])
        is_pasted_content = (has_resume_keywords or was_prompted_for_resume or len(text.split()) > 20) and not is_asking_how

        field_name = active_career.title() if active_career else "your target field"
        if is_pasted_content:
            return (
                f"### 📄 Structured Resume Review (Tailored for {field_name})\n\n"
                f"Here is an actionable, ATS-friendly assessment of the resume content you provided:\n\n"
                f"#### 1. Identified Strengths\n"
                f"• **Clear Direction:** The profile communicates identifiable domain focus relevant to {field_name}.\n"
                f"• **Core Sections Present:** Includes essential foundational elements (education, skills, and background).\n\n"
                f"#### 2. Key Areas for Improvement\n"
                f"• **Impact & Quantification:** Replace vague descriptions with measurable outcomes.\n"
                f"  *(Example: Instead of 'Worked on site project', use 'Assisted site engineer in daily quality inspections and slump testing for a 5-story reinforced concrete structure'.)*\n"
                f"• **Action Verbs:** Start bullet points with strong verbs (*Designed, Analyzed, Executed, Supervised, Formulated, Coordinated*).\n\n"
                f"#### 3. Essential Industry Sections Checklist\n"
                f"• [x] Contact Information (Full Name, Professional Email, Phone, LinkedIn/Portfolio)\n"
                f"• [x] Domain-Specific Skills (Categorized by Core Competencies & Industry Software/Tools)\n"
                f"• [ ] **Practical Experience / Capstone Projects** (Include methodology, software used, and verifiable outcomes)\n"
                f"• [ ] Education & Accredited Certifications (Verified credentials only)\n\n"
                f"#### 4. Professional Integrity & ATS Best Practices\n"
                f"• Maintain clean, single-column formatting without tables or graphic elements that disrupt automated applicant tracking systems.\n"
                f"• **Ethical Standard:** Never fabricate credentials, employment dates, or responsibilities. Verifiable projects carry high credibility.\n\n"
                f"**SDG 8 Connection:** Honest, transparent presentation of capabilities supports fair hiring and productive employment.\n\n"
                f"**Next step:** Would you like to refine the bullet points for a specific project or internship experience?"
            )
        else:
            return (
                f"### 📄 Resume Improvement Guidance for {field_name}\n\n"
                f"A strong, professional resume is your key to securing interviews and internships in **{field_name}**:\n\n"
                f"1. **Header:** Name, City/Location, Professional Email, Phone, and LinkedIn or Portfolio link.\n"
                f"2. **Education:** Degree/Diploma, Major, Institution, expected completion year, and GPA/Percentage.\n"
                f"3. **Domain Skills:** Specific technical tools (e.g. AutoCAD, SolidWorks, Excel, Figma, etc.) and core knowledge areas.\n"
                f"4. **Practical Experience & Projects:** 2–3 structured descriptions using the formula:\n"
                f"   > **[Action Verb]** + **[Task/Challenge]** + **[Tools/Methods Used]** + **[Measurable Outcome]**\n"
                f"5. **Certifications & Licensure:** Verified professional credentials, workshops, or academic honors.\n\n"
                f"**How I can help:** Paste your resume bullet points or profile summary here, and I will give you honest, structured feedback!\n\n"
                f"**Next step:** Paste 2-3 bullet points from your current resume for review."
            )

    # 8. Career Comparisons (e.g. Python vs Java, Civil vs Mechanical, etc.)
    if " vs " in lower or "versus" in lower or "which is better" in lower:
        if "civil" in lower and "mechanical" in lower:
            return (
                "### ⚖️ Career Comparison: Civil Engineering vs. Mechanical Engineering\n\n"
                "Both are foundational engineering disciplines driving physical infrastructure and industrial growth (SDG 8):\n\n"
                "| Dimension | Civil Engineering | Mechanical Engineering |\n"
                "| :--- | :--- | :--- |\n"
                "| **Primary Focus** | Buildings, bridges, transport, water resources, urban infrastructure | Machines, thermal systems, manufacturing, automotive, robotics |\n"
                "| **Core Work Environment** | Split between design offices and active construction/field sites | Design offices, manufacturing plants, laboratories, and testing floors |\n"
                "| **Primary Software** | AutoCAD, STAAD Pro, Revit, Civil 3D, ETABS | SolidWorks, CATIA, ANSYS, Creo, MATLAB/Simulink |\n"
                "| **Major Employers** | Infrastructure builders (L&T, Shapoorji), public works (PWD/NHAI), consultancies | Automotive OEMs (Tata, Ford), aerospace, heavy manufacturing, energy firms |\n"
                "| **SDG 8 Impact** | Sustainable cities, clean water systems, resilient infrastructure | Industrial innovation, energy efficiency, advanced manufacturing |\n\n"
                "**Recommendation:**\n"
                "• Choose **Civil Engineering** if you enjoy large-scale structures, town planning, and site management.\n"
                "• Choose **Mechanical Engineering** if you love mechanisms, thermodynamics, machine design, and robotics.\n\n"
                "**Next step:** Which of these environments (infrastructure sites vs machine design) appeals to you more?"
            )
        elif "python" in lower and "java" in lower:
            return (
                "### ⚖️ Career & Skills Comparison: Python vs. Java\n\n"
                "Both Python and Java are top-tier industry languages, but they align with different career pathways. "
                "Neither is universally 'better'; your choice should reflect your target domain:\n\n"
                "| Dimension | Python | Java |\n"
                "| :--- | :--- | :--- |\n"
                "| **Core Domains** | AI/ML, Data Science, Scripting, Fast Web APIs | Enterprise Backend, Android, Large Distributed Systems |\n"
                "| **Syntax & Curve** | Minimal, intuitive syntax; faster initial learning | Strict, statically typed, enforces OOP rigor |\n"
                "| **Execution Speed** | Interpreted; optimized via C/C++ libraries (NumPy) | Compiled to bytecode (JVM); high performance |\n"
                "| **Job Market** | High demand in AI, startups, analytics, cloud | High demand in banking, enterprise services, large tech |\n"
                "| **SDG 8 Impact** | Accessible entry point for digital skills training | Industry-standard stability for large economic systems |\n\n"
                "**Recommendation based on your goals:**\n"
                "• **Choose Python** if you want to explore Data Science, AI/ML, automation, or rapid prototyping.\n"
                "• **Choose Java** if your goal is enterprise software engineering, robust distributed backends, or corporate campus placements.\n\n"
                "**Next step:** Which of these career directions interests you more?"
            )

    # 9. Acknowledging Active Career Goal
    if active_career:
        return (
            f"### 🎯 Focus: **{active_career.title()}**\n\n"
            f"Targeting a career in **{active_career.title()}** is an impactful and practical goal aligned with SDG 8. "
            f"Here is how we can accelerate your preparation:\n\n"
            f"1. **Structured Roadmap:** I can generate a tailored, step-by-step roadmap from your current education level to entry-level employment.\n"
            f"2. **Skill Benchmarking:** Compare the top tools and core competencies required by employers in {active_career.title()}.\n"
            f"3. **Internship Strategy:** Identify high-value internships, site training, or practicum opportunities.\n"
            f"4. **Mock Interview:** Practice field-specific technical and situational interview questions.\n\n"
            f"**Next step:** What would you like to explore first: a step-by-step roadmap, required skills, or internship strategies?"
        )

    # 10. Universal Career Guidance Fallback (Never return the static Welcome message in a chat response!)
    return (
        "### 🧭 Career Guidance & Employability Planning\n\n"
        "I am ready to help you navigate your educational pathway, build in-demand skills, and achieve decent, "
        "sustainable employment aligned with **UN SDG 8: Decent Work & Economic Growth**.\n\n"
        "I support career exploration across **all fields and industries**:\n"
        "• 🏗️ **Engineering & Infrastructure:** Civil, Mechanical, Electrical, Architecture\n"
        "• 💊 **Healthcare & Life Sciences:** Pharmacy, Medicine, Nursing, Public Health\n"
        "• ⚖️ **Law & Public Administration:** Legal Practice, Civil Services (UPSC), SSC, Banking\n"
        "• 📚 **Education & Academics:** School Teaching, College Professorship, Research\n"
        "• 🎨 **Design & Creative Arts:** Graphic Design, UI/UX, Multimedia, Content\n"
        "• 💼 **Commerce & Management:** Corporate Finance, Accounting, Marketing, HR\n"
        "• 💻 **Technology & Computing:** Software Engineering, Data Science, AI, Cloud\n\n"
        "**To give you tailored advice:** What career or field of study would you like to explore today?"
    )

def call_gemini_api(prompt: str) -> Optional[str]:
    """Calls Google Gemini API if key is available."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip() or GEMINI_API_KEY
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        for model_name in ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_PROMPT
                )
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                logger.warning(f"Gemini model {model_name} attempt failed: {e}")
                continue
    except Exception as e:
        logger.error(f"Gemini API initialization/execution error: {e}")
    return None

def call_openai_api(messages: List[Dict[str, str]]) -> Optional[str]:
    """Calls OpenAI API if key is available."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip() or os.environ.get("LLM_API_KEY", "").strip() or OPENAI_API_KEY or GENERIC_LLM_KEY
    if not api_key:
        return None
    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1200
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.warning(f"OpenAI API returned non-200 status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"OpenAI API execution error: {e}")
    return None

def process_chat_message(session_id: str, message: str) -> Dict[str, Any]:
    """
    Main processing pipeline for general career assistance:
    1. Input validation
    2. Context & career extraction across all disciplines and languages
    3. Responsible AI Guardrails & Scope check
    4. LLM generation with multi-career fallback engine
    5. Memory update & snapshot creation
    """
    if not message or not message.strip():
        return {
            "error": "Message cannot be empty",
            "session_id": session_id,
            "status_code": 400
        }

    clean_message = message.strip()

    # Update structured context from user message
    memory_store.extract_and_update_context(session_id, clean_message)
    user_context = memory_store.get_user_context(session_id)

    # Check Guardrails & Scope
    is_handled, guardrail_response = check_guardrails(clean_message)
    if is_handled and guardrail_response:
        memory_store.add_message(session_id, "user", clean_message)
        memory_store.add_message(session_id, "assistant", guardrail_response)
        snapshot = generate_readiness_snapshot(user_context)
        return {
            "response": guardrail_response,
            "session_id": session_id,
            "readiness_snapshot": snapshot,
            "status_code": 200
        }

    # Retrieve recent history (sliding window)
    history = memory_store.get_recent_messages(session_id, limit=14)
    context_str = format_context_prompt(user_context)

    response_text = None

    # Try external LLM if credentials exist
    if GEMINI_API_KEY:
        full_prompt = (
            f"User Profile Context:\n{context_str}\n\n"
            f"Recent Conversation History:\n"
        )
        for h in history[-8:]:
            full_prompt += f"{h['role'].capitalize()}: {h['content']}\n"
        full_prompt += f"User: {clean_message}\nAssistant:"
        response_text = call_gemini_api(full_prompt)

    if not response_text and (OPENAI_API_KEY or GENERIC_LLM_KEY):
        llm_messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nUser Context:\n{context_str}"}]
        for h in history[-8:]:
            llm_messages.append({"role": h["role"], "content": h["content"]})
        llm_messages.append({"role": "user", "content": clean_message})
        response_text = call_openai_api(llm_messages)

    # If no LLM available or LLM failed, utilize multi-career knowledge engine
    if not response_text:
        response_text = generate_local_engine_response(clean_message, session_id, user_context, history)

    # Record message turns
    memory_store.add_message(session_id, "user", clean_message)
    memory_store.add_message(session_id, "assistant", response_text)

    # Generate Career Readiness Snapshot
    snapshot = generate_readiness_snapshot(user_context)

    return {
        "response": response_text,
        "session_id": session_id,
        "readiness_snapshot": snapshot,
        "status_code": 200
    }
