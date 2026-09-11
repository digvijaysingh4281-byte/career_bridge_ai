"""
CareerBridge AI - SQLite Persistent Conversation Memory & Context Management
General-purpose career guidance aligned with UN SDG 8: Decent Work and Economic Growth.
"""
import os
import sqlite3
import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_FILE = os.environ.get("DATABASE_PATH", "data/careerbridge.db")

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_db_connection():
    """Returns a SQLite connection with row factory enabled."""
    db_dir = os.path.dirname(DB_FILE)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception:
            pass
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    except Exception:
        conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

class ConversationMemory:
    def __init__(self, db_conn=None):
        self.conn = db_conn or get_db_connection()
        self._init_db()

    def _init_db(self):
        """Initializes tables for sessions and messages."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                education_level TEXT,
                field TEXT,
                career_interest TEXT,
                experience_level TEXT,
                skills TEXT,
                career_goal TEXT,
                preferred_learning_style TEXT,
                location TEXT,
                interview_mode INTEGER DEFAULT 0,
                interview_role TEXT DEFAULT '',
                interview_question_idx INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        self.conn.commit()

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieves or creates a session record."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        now = _now_iso()
        if not row:
            cursor.execute("""
                INSERT INTO sessions (
                    session_id, created_at, updated_at,
                    education_level, field, career_interest, experience_level,
                    skills, career_goal, preferred_learning_style, location,
                    interview_mode, interview_role, interview_question_idx
                ) VALUES (?, ?, ?, '', '', '', '', '[]', '', '', '', 0, '', 0)
            """, (session_id, now, now))
            self.conn.commit()
            return self.get_or_create_session(session_id)

        session_dict = dict(row)
        try:
            session_dict["skills"] = json.loads(session_dict.get("skills") or "[]")
        except Exception:
            session_dict["skills"] = []
        return session_dict

    def add_message(self, session_id: str, role: str, content: str):
        """Appends a message to the session history."""
        self.get_or_create_session(session_id)
        now = _now_iso()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, now))
        cursor.execute("UPDATE sessions SET updated_at = ? WHERE session_id = ?", (now, session_id))
        self.conn.commit()

    def get_recent_messages(self, session_id: str, limit: int = 20) -> List[Dict[str, str]]:
        """Returns the most recent messages up to the context window limit."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT role, content FROM messages
            WHERE session_id = ?
            ORDER BY id DESC LIMIT ?
        """, (session_id, limit))
        rows = cursor.fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def get_user_context(self, session_id: str) -> Dict[str, Any]:
        """Returns extracted structured context for the session."""
        session = self.get_or_create_session(session_id)
        return {
            "education_level": session.get("education_level", ""),
            "field": session.get("field", ""),
            "career_interest": session.get("career_interest", ""),
            "experience_level": session.get("experience_level", ""),
            "skills": session.get("skills", []),
            "career_goal": session.get("career_goal", ""),
            "preferred_learning_style": session.get("preferred_learning_style", ""),
            "location": session.get("location", ""),
            "interview_mode": bool(session.get("interview_mode", 0)),
            "interview_role": session.get("interview_role", ""),
            "interview_question_idx": session.get("interview_question_idx", 0),
        }

    def update_user_context(self, session_id: str, **kwargs):
        """Updates specific fields in the session context."""
        self.get_or_create_session(session_id)
        valid_fields = [
            "education_level", "field", "career_interest", "experience_level",
            "skills", "career_goal", "preferred_learning_style", "location",
            "interview_mode", "interview_role", "interview_question_idx"
        ]
        updates = []
        values = []
        for k, v in kwargs.items():
            if k in valid_fields:
                if k == "skills" and isinstance(v, list):
                    v = json.dumps(list(dict.fromkeys(v)))
                elif k == "interview_mode":
                    v = 1 if v else 0
                updates.append(f"{k} = ?")
                values.append(v)
        if updates:
            values.append(_now_iso())
            values.append(session_id)
            query = f"UPDATE sessions SET {', '.join(updates)}, updated_at = ? WHERE session_id = ?"
            cursor = self.conn.cursor()
            cursor.execute(query, tuple(values))
            self.conn.commit()

    def reset_session(self, session_id: str):
        """Resets the conversation messages and context for a session."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        self.conn.commit()
        self.get_or_create_session(session_id)

    def extract_and_update_context(self, session_id: str, message: str):
        """
        Extracts user profile details across general careers and multilingual input (English, Hindi, Gujarati).
        Does NOT assume or default to software or AI careers.
        """
        text = message.strip()
        lower = text.lower()
        context = self.get_user_context(session_id)
        updates = {}

        # 1. Education Level
        edu_match = re.search(
            r"\b(first|second|third|fourth|final|1st|2nd|3rd|4th)[\s-]year\b.*?(cse|cs|it|engineering|college|student)?",
            lower
        )
        if edu_match:
            updates["education_level"] = f"{edu_match.group(1)}-year student"
        elif "after 12th" in lower or "after class 12" in lower or "12th passed" in lower:
            updates["education_level"] = "12th standard graduate"
        elif "fresh graduate" in lower or "fresh grad" in lower or "recent graduate" in lower:
            updates["education_level"] = "fresh graduate"
        elif "college student" in lower:
            updates["education_level"] = "college student"
        elif "high school" in lower or "school student" in lower:
            updates["education_level"] = "high school student"

        # 2. Field of Study / Academic Background
        if re.search(r"\b(civil engineering|civil engineer|civil)\b", lower) and "engineering" in lower:
            updates["field"] = "Civil Engineering"
        elif re.search(r"\b(mechanical engineering|mechanical engineer|mech)\b", lower):
            updates["field"] = "Mechanical Engineering"
        elif re.search(r"\b(electrical engineering|electrical engineer|eee)\b", lower):
            updates["field"] = "Electrical Engineering"
        elif re.search(r"\b(electronics|ece)\b", lower):
            updates["field"] = "Electronics & Communication Engineering"
        elif re.search(r"\b(b\.?tech cse|btech cse|cse|computer science engineering|computer science & engineering|computer science|cs)\b", lower):
            updates["field"] = "B.Tech Computer Science & Engineering (CSE)"
        elif re.search(r"\b(information technology|it)\b", lower):
            updates["field"] = "Information Technology"
        elif re.search(r"\b(medical|medicine|mbbs|healthcare)\b", lower):
            updates["field"] = "Medicine & Healthcare"
        elif re.search(r"\b(law|legal studies|llb)\b", lower):
            updates["field"] = "Law & Legal Studies"
        elif re.search(r"\b(architecture|b\.arch)\b", lower):
            updates["field"] = "Architecture"
        elif re.search(r"\b(commerce|bcom|bba|business|accounting|finance)\b", lower):
            updates["field"] = "Commerce & Finance"
        elif re.search(r"\b(teaching|b\.ed|education)\b", lower):
            updates["field"] = "Education & Pedagogy"
        elif re.search(r"\b(design|graphic design|fine arts)\b", lower):
            updates["field"] = "Design & Creative Arts"

        # 3. Dynamic Career Interest / Goal Extraction
        detected_career = None

        # Direct Domain Keyword Matching (High priority)
        if re.search(r"\b(b\.?tech cse|btech cse|computer science engineering|cse)\b", lower):
            detected_career = "B.Tech CSE"
        elif re.search(r"\b(pharmacy|pharmacist|b\.?pharm|d\.?pharm|m\.?pharm|pharm\.?d|pharmaceutical)\b", lower):
            detected_career = "Pharmacy"
        elif re.search(r"\b(civil engineering|civil engineer)\b", lower) or ("civil" in lower and any(w in lower for w in ["engineering", "roadmap", "site", "construction", "banna", "banva"])):
            detected_career = "Civil Engineering"
        elif re.search(r"\b(mechanical engineering|mechanical engineer)\b", lower) or ("mechanical" in lower and any(w in lower for w in ["engineering", "roadmap", "cad", "banna", "banva"])):
            detected_career = "Mechanical Engineering"
        elif re.search(r"\b(electrical engineering|electrical engineer|eee)\b", lower):
            detected_career = "Electrical Engineering"
        elif re.search(r"\b(doctor|physician|surgeon|mbbs|medicine|medical)\b", lower) and not any(w in lower for w in ["kit", "supplies"]):
            detected_career = "Doctor (Medicine)"
        elif re.search(r"\b(nursing|nurse|b\.?sc nursing)\b", lower):
            detected_career = "Nursing"
        elif re.search(r"\b(lawyer|advocate|law|legal professional|llb)\b", lower):
            detected_career = "Lawyer (Legal Practice)"
        elif re.search(r"\b(teacher|professor|lecturer|teaching|educator|b\.?ed)\b", lower):
            detected_career = "Teacher / Educator"
        elif re.search(r"\b(architect|architecture|b\.?arch)\b", lower):
            detected_career = "Architect"
        elif re.search(r"\b(graphic designer|graphic design|ui/ux designer|ui/ux)\b", lower):
            detected_career = "Graphic Designer"
        elif re.search(r"\b(finance|investment banking|chartered accountant|ca|accounting|accountant|banker)\b", lower) and any(w in lower for w in ["work", "career", "become", "field", "roadmap", "job", "in finance"]):
            detected_career = "Finance & Accounting"
        elif re.search(r"\b(government job|government jobs|upsc|civil services|ias|ips|ssc|sarkari)\b", lower):
            detected_career = "Government & Civil Services"
        elif re.search(r"\b(journalism|journalist|mass communication|media reporter)\b", lower):
            detected_career = "Journalism & Media"
        elif re.search(r"\b(agriculture|agricultural engineering|agri|farming)\b", lower):
            detected_career = "Agriculture & Agri-Tech"
        elif re.search(r"\b(hospitality|hotel management|culinary|chef|tourism)\b", lower):
            detected_career = "Hospitality & Tourism"
        elif re.search(r"\b(ai engineer|machine learning engineer)\b", lower):
            detected_career = "AI Engineer"
        elif re.search(r"\b(data scientist|data science)\b", lower):
            detected_career = "Data Scientist"
        elif re.search(r"\b(data analyst)\b", lower):
            detected_career = "Data Analyst"
        elif re.search(r"\b(software engineer|software developer|full stack|backend developer|frontend developer)\b", lower):
            detected_career = "Software Engineer"

        # Multilingual: Hindi ("mujhe civil engineer banna hai", "main doctor banna chahta hoon")
        if not detected_career:
            hindi_match = re.search(
                r"(?:mujhe|mai|main)\s+([a-zA-Z\s]+?)\s+(?:banna\s+hai|banna\s+chahta\s+hoon|banna\s+chahti\s+hoon|banna\s+chahta|ki\s+taiyari)",
                text, re.IGNORECASE
            )
            if hindi_match:
                detected_career = hindi_match.group(1).strip()

        # Multilingual: Gujarati ("hu mechanical engineer banva maangu chu", "doctor banvu che")
        if not detected_career:
            guj_match = re.search(
                r"(?:hu|mane)\s+([a-zA-Z\s]+?)\s+(?:banva\s+maangu\s+chu|banvu\s+che|banvu\s+hoi)",
                text, re.IGNORECASE
            )
            if guj_match:
                detected_career = guj_match.group(1).strip()

        # Natural Language Roadmap/Career queries ("explain roadmap in pharmacy", "career in X", "roadmap for X")
        if not detected_career:
            roadmap_match = re.search(
                r"\b(?:roadmap|pathway|guide|steps|scope|career|how to become)\s+(?:in|for|of|to|as)?\s+(?:an?\b|the\b)?\s*([a-zA-Z\s\/\+\-]+?)(?:\.|\?|$|,|\bfor\b|\band\b)",
                text, re.IGNORECASE
            )
            if roadmap_match:
                candidate = roadmap_match.group(1).strip()
                candidate = re.sub(r"^(?:an|a|the)\s+", "", candidate, flags=re.IGNORECASE).strip()
                if 2 < len(candidate) < 35 and not any(w in candidate.lower() for w in ["detail", "general", "first", "good", "help", "interview", "skills", "roadmap"]):
                    detected_career = candidate.title()

        # General English intent regex ("want to become X", "aspire to be X")
        if not detected_career:
            intent_match = re.search(
                r"\b(?:want to (?:become|be|work as)|aspire to be|aiming (?:to be|for)|career in|looking to (?:be|become|work in)|work in|pursuing a career in|prepare for)\s+(?:an?\b|the\b)?\s*([a-zA-Z\s\/\+\-]+?)(?:\.|$|,|\bfor\b|\band\b)",
                text, re.IGNORECASE
            )
            if intent_match:
                candidate = intent_match.group(1).strip()
                candidate = re.sub(r"^(?:an|a|the)\s+", "", candidate, flags=re.IGNORECASE).strip()
                if 2 < len(candidate) < 40 and not any(w in candidate.lower() for w in ["job", "first", "good", "help", "interview", "skills", "roadmap"]):
                    detected_career = candidate.title()

        if detected_career:
            updates["career_interest"] = detected_career
            updates["career_goal"] = detected_career
            if not updates.get("field"):
                updates["field"] = detected_career

        # 4. Experience Level
        if "beginner" in lower or "starting out" in lower or "no prior experience" in lower or "from scratch" in lower:
            updates["experience_level"] = "Beginner"
        elif "intermediate" in lower or "some experience" in lower:
            updates["experience_level"] = "Intermediate"
        elif "advanced" in lower or "senior" in lower or "years of experience" in lower:
            updates["experience_level"] = "Advanced"

        # 5. Skills Extraction across disciplines
        current_skills = set(context.get("skills", []))
        SKILL_DICTIONARY = [
            # Civil, Mechanical, Architecture
            "AutoCAD", "SolidWorks", "Revit", "STAAD Pro", "Civil 3D", "CATIA", "ANSYS",
            "Surveying", "Total Station", "Structural Analysis", "Thermodynamics", "Fluid Mechanics",
            "Construction Management", "Building Codes", "BIM", "Architectural Drafting",
            # Design & Creative
            "Figma", "Photoshop", "Illustrator", "Typography", "Branding", "Wireframing",
            "InDesign", "Blender", "Color Theory", "UI/UX Design",
            # Finance & Commerce
            "Financial Modeling", "Excel", "Tally", "Financial Accounting", "Valuation",
            "Corporate Finance", "Taxation", "Auditing", "SAP",
            # Medicine & Healthcare
            "Clinical Diagnosis", "Patient Care", "Anatomy", "Pharmacology", "Medical Ethics", "First Aid",
            # Law & Teaching
            "Legal Research", "Legal Drafting", "Moot Court", "Constitutional Law",
            "Pedagogy", "Classroom Management", "Curriculum Planning",
            # Technology & Data
            "Python", "SQL", "Java", "C++", "C", "JavaScript", "TypeScript",
            "HTML", "CSS", "React", "Node.js", "Django", "FastAPI", "Pandas", "NumPy",
            "Scikit-Learn", "Git", "GitHub", "Docker", "AWS", "Linux"
        ]

        knows_pattern = re.search(r"\b(i know|i have learned|skills are|skilled in|familiar with|worked with|proficient in|experience with)\s+([^.]+)", lower)
        search_domain = knows_pattern.group(2) if knows_pattern else lower

        for skill in SKILL_DICTIONARY:
            skill_pattern = r"\b" + re.escape(skill.lower()) + r"\b"
            if re.search(skill_pattern, search_domain):
                current_skills.add(skill)

        if current_skills:
            updates["skills"] = sorted(list(current_skills))

        # 6. Interview Mode Trigger (dynamic across fields)
        interview_explicit = re.search(r"\b(?:interview me for|prepare an interview for|mock interview for)\s*(?:a|an)?\s*([a-zA-Z\s\/\-]+)", text, re.IGNORECASE)
        general_interview_trigger = re.search(r"\b(take my mock interview|interview me|start mock interview|can you prepare an interview)\b", lower)

        if interview_explicit:
            role = interview_explicit.group(1).strip()
            updates["interview_mode"] = 1
            updates["interview_role"] = role
            updates["interview_question_idx"] = 1
        elif general_interview_trigger:
            role = context.get("career_interest") or context.get("career_goal") or updates.get("career_interest") or "General Employability"
            updates["interview_mode"] = 1
            updates["interview_role"] = role
            updates["interview_question_idx"] = 1

        if updates:
            self.update_user_context(session_id, **updates)

# Global singleton
memory_store = ConversationMemory()
