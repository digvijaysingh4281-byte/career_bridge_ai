"""
CareerBridge AI - Career Readiness Snapshot Generator
Innovation Feature: Visual skill-gap and stage estimator aligned with SDG 8.
Supports diverse professions: Engineering, Healthcare, Law, Teaching, Design, Finance, Public Sector, and Tech.
"""
from typing import Dict, Any, List, Optional

BENCHMARK_SKILLS = {
    "civil engineering": [
        "Engineering Drawing & AutoCAD", "Structural Analysis (STAAD Pro)",
        "Surveying & Total Station", "Building Materials & Concrete Technology",
        "Geotechnical & Soil Mechanics", "Construction Management & Site Safety",
        "BIM / Revit Basics", "Site Internship & Field Exposure"
    ],
    "mechanical engineering": [
        "Engineering Mechanics & Strength of Materials", "Thermodynamics & Heat Transfer",
        "3D CAD Modeling (SolidWorks/CATIA)", "Manufacturing Processes & CNC",
        "Fluid Mechanics & Hydraulics", "Finite Element Analysis (ANSYS)",
        "Industrial Internship & Workshop Practice", "Quality & Safety Standards (SDG 8)"
    ],
    "electrical engineering": [
        "Circuit Theory & Analysis", "Electrical Machines & Transformers",
        "Power Systems & Distribution", "Control Systems & MATLAB/Simulink",
        "Power Electronics & Drives", "Renewable Energy Systems",
        "Industrial Safety & Grid Standards", "Practical Lab / Plant Internship"
    ],
    "doctor": [
        "Pre-Med Entrance (NEET/MCAT)", "Human Anatomy & Physiology",
        "Biochemistry & Pharmacology", "Pathology & Microbiology",
        "Clinical Examination & Patient Triage", "Medical Ethics & Evidence-based Practice",
        "Hospital Internship (Rotatory Housemanship)", "Statutory Licensing / Medical Council Registration"
    ],
    "medicine": [
        "Human Anatomy & Physiology", "Biochemistry & Pharmacology",
        "Pathology & Microbiology", "Clinical Diagnosis & Patient Care",
        "Medical Ethics & Jurisprudence", "Hospital Rotations / Clinical Postings",
        "Residency / Housemanship", "Board Licensing"
    ],
    "lawyer": [
        "Constitutional & Administrative Law", "Criminal & Civil Procedure Codes",
        "Legal Research & Case Briefing", "Legal Drafting & Conveyancing",
        "Moot Court & Trial Advocacy", "Statutory Interpretation",
        "Internship with Chambers / Law Firm", "Bar Council Licensing Examination"
    ],
    "law": [
        "Constitutional Law & Jurisprudence", "Contract & Commercial Law",
        "Legal Research & Case Analysis", "Legal Drafting & Pleadings",
        "Moot Court & Client Counseling", "Law Firm / Judicial Internship",
        "Bar Licensing & Professional Ethics"
    ],
    "teacher": [
        "Subject-Matter Mastery", "Educational Psychology & Child Development",
        "Pedagogical Strategies & Lesson Planning", "Classroom Management & Inclusion",
        "Assessment & Evaluation Techniques", "Educational Technology & Digital Tools",
        "Teaching Practicum / School Internship", "Teaching Eligibility Certification (TET/B.Ed)"
    ],
    "teaching": [
        "Subject-Matter Depth", "Pedagogy & Instructional Design",
        "Classroom Management", "Curriculum Development",
        "Student Evaluation & Feedback", "School Practicum / Student Teaching",
        "Professional Educator Certification"
    ],
    "architect": [
        "Architectural Drafting & Freehand Sketching", "AutoCAD & Building By-Laws",
        "3D BIM Modeling (Revit / Rhino / SketchUp)", "Structural Concepts & Building Materials",
        "Sustainable & Climatological Design", "Rendering & Visual Presentation",
        "Design Studio Portfolio", "Council of Architecture Registration"
    ],
    "architecture": [
        "Architectural Design & Space Planning", "AutoCAD & 3D Modeling (Revit)",
        "Building Construction & Materials", "Sustainable Architecture",
        "Design Portfolio & Juried Reviews", "Professional Architectural Internship",
        "Architectural Licensing"
    ],
    "graphic designer": [
        "Design Principles & Visual Hierarchy", "Typography & Color Theory",
        "Industry Tools (Adobe Photoshop, Illustrator)", "UI/UX & Prototyping (Figma)",
        "Brand Identity & Logo Systems", "Layout Design (InDesign)",
        "Creative Portfolio (Behance / Dribbble)", "Client Communication & Freelance Practice"
    ],
    "graphic design": [
        "Visual Composition & Layout", "Typography & Color Systems",
        "Vector Illustration & Photo Editing", "UI/UX Basics & Figma",
        "Branding & Visual Storytelling", "Professional Design Portfolio",
        "Production & Digital Asset Delivery"
    ],
    "finance": [
        "Financial Accounting & Reporting", "Corporate Finance & Working Capital",
        "Advanced Excel & Financial Modeling", "Financial Statement Analysis",
        "Valuation & Investment Appraisal", "Regulatory Compliance & Taxation",
        "Banking / Financial Institution Internship", "Professional Certification (CFA/CA/CPA/FRM)"
    ],
    "government": [
        "General Studies & Current Affairs", "Quantitative Aptitude & Mathematics",
        "Logical & Analytical Reasoning", "Constitutional Law & Governance",
        "Public Administration & Ethics", "Essay & Descriptive Writing",
        "Mock Test Series & Time Management", "Interview / Personality Test Preparation"
    ],
    "pharmacist": [
        "Pharmaceutical Chemistry & Medicinal Chemistry", "Pharmacology & Toxicology",
        "Pharmaceutics & Drug Formulation", "Pharmacokinetics & Dosage Calculations",
        "Clinical Pharmacy & Patient Counseling", "Hospital & Community Pharmacy Practice",
        "Drug Regulatory Affairs & GMP", "State Pharmacy Council Licensing (Registered Pharmacist)"
    ],
    "pharmacy": [
        "Human Anatomy, Physiology & Pathology", "Pharmacology & Pharmacotherapeutics",
        "Pharmaceutics & Dispensing Practice", "Pharmaceutical Analysis & Quality Control",
        "Clinical & Hospital Pharmacy Postings", "Pharmacovigilance & Drug Safety",
        "Community Pharmacy & Patient Counseling", "Pharmacy Council Registration"
    ],
    "btech cse": [
        "Data Structures & Algorithms (DSA)", "Object-Oriented Programming (Java/C++/Python)",
        "Database Management Systems (DBMS & SQL)", "Operating Systems & Linux Shell",
        "Computer Networks & Protocols", "Version Control (Git & GitHub)",
        "Full-Stack Web Dev / Cloud / System Projects", "Tech Internship & Coding Problem Solving"
    ],
    "b.tech cse": [
        "Data Structures & Algorithms (DSA)", "Object-Oriented Programming (Java/C++/Python)",
        "Database Management Systems (DBMS & SQL)", "Operating Systems & Linux Shell",
        "Computer Networks & Protocols", "Version Control (Git & GitHub)",
        "Full-Stack Web Dev / Cloud / System Projects", "Tech Internship & Coding Problem Solving"
    ],
    "cse": [
        "Data Structures & Algorithms (DSA)", "OOP Concepts (Java/C++)",
        "DBMS & Relational Databases (SQL)", "Operating Systems & System Calls",
        "Computer Networks (TCP/IP, HTTP)", "Git/GitHub & Collaborative Coding",
        "Applied Capstone Project", "Software Engineering Best Practices (SDG 8)"
    ],
    "ai engineer": [
        "Python Programming", "Mathematics & Statistics for ML",
        "Data Structures & Algorithms", "Pandas & NumPy", "Scikit-Learn",
        "Deep Learning (PyTorch/TF)", "Git/GitHub", "Model Deployment (FastAPI/Docker)"
    ],
    "software engineer": [
        "Core Programming Language", "Data Structures & Algorithms",
        "Object-Oriented Design", "Databases (SQL/NoSQL)", "Git/GitHub",
        "Unit Testing & Debugging", "Web Architecture & APIs", "Production Projects"
    ]
}

DEFAULT_BENCHMARK = [
    "Core Domain Knowledge & Principles", "Industry Software, Tools & Methodology",
    "Applied Practical Project or Fieldwork", "Professional Communication & Teamwork",
    "Workplace Safety, Ethics & Standards (SDG 8)", "Industry Portfolio or Professional Certification"
]

def generate_readiness_snapshot(user_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generates a structured Career Readiness Snapshot dynamically mapped
    to the user's specific career field (Engineering, Healthcare, Law, Teaching, Design, etc.).
    """
    target = user_context.get("career_interest") or user_context.get("career_goal") or ""
    current_skills: List[str] = user_context.get("skills", [])
    edu = user_context.get("education_level") or "Student / Learner"

    # Only generate snapshot if we have at least a target role or known skills
    if not target and not current_skills:
        return None

    norm_target = target.lower().strip()
    matched_benchmark = None

    # Search for matching benchmark
    for role_key, benchmark in BENCHMARK_SKILLS.items():
        if role_key in norm_target or norm_target in role_key:
            matched_benchmark = benchmark
            break

    if not matched_benchmark:
        matched_benchmark = DEFAULT_BENCHMARK

    # Identify strengths (skills present in user context, case-insensitive match)
    norm_current_skills = {s.lower(): s for s in current_skills}
    strengths = []
    recommended_next = []

    for item in matched_benchmark:
        matched = False
        for cur_lower, cur_orig in norm_current_skills.items():
            if cur_lower in item.lower() or item.lower() in cur_lower:
                strengths.append(cur_orig)
                matched = True
                break
        if not matched:
            recommended_next.append(item)

    # Any remaining current skills not in benchmark are also strengths
    for cur_lower, cur_orig in norm_current_skills.items():
        if cur_orig not in strengths:
            strengths.append(cur_orig)

    # Calculate learning progress estimate
    total_milestones = max(len(matched_benchmark), 1)
    matching_strengths = len([s for s in strengths if any(b.lower() in s.lower() or s.lower() in b.lower() for b in matched_benchmark)])
    estimated_readiness_pct = min(int((matching_strengths / total_milestones) * 100), 95)
    if strengths and estimated_readiness_pct < 15:
        estimated_readiness_pct = 20

    # Determine stage
    if estimated_readiness_pct < 30:
        current_stage = "Stage 1: Foundations & Core Concepts"
    elif estimated_readiness_pct < 65:
        current_stage = "Stage 2: Applied Skills & Practicum"
    elif estimated_readiness_pct < 85:
        current_stage = "Stage 3: Advanced Training & Experience"
    else:
        current_stage = "Stage 4: Professional & Interview Readiness"

    return {
        "target_role": target.title() if target else "General Professional Path",
        "education_level": edu,
        "current_strengths": strengths if strengths else ["Active exploration underway"],
        "recommended_next": recommended_next[:5],
        "estimated_readiness_pct": estimated_readiness_pct,
        "current_stage": current_stage,
        "disclaimer": "AI-generated learning readiness estimate. Not a formal psychometric or certified hiring evaluation.",
        "sdg_alignment": "SDG 8: Skills development for decent, productive employment."
    }
