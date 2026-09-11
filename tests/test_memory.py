"""
Tests for Conversational Memory, Multi-turn Context, and General Multi-Career Scenarios
"""
import uuid
import pytest
from app.backend.chatbot import process_chat_message
from app.backend.memory import memory_store

def test_test1_civil_engineering_roadmap():
    """TEST 1: 'I want to become a civil engineer. Give me a roadmap.' -> Civil Engineering roadmap."""
    session_id = f"test-civil-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I want to become a civil engineer. Give me a roadmap.")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "civil engineering" in ans
    assert "autocad" in ans or "staad pro" in ans or "construction" in ans or "surveying" in ans
    # Check that snapshot updated to Civil Engineering
    ctx = memory_store.get_user_context(session_id)
    assert "civil" in ctx["career_interest"].lower()

def test_test2_mechanical_engineering():
    """TEST 2: 'I want to become a mechanical engineer.' -> Mechanical Engineering guidance."""
    session_id = f"test-mech-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I want to become a mechanical engineer.")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "mechanical engineering" in ans or "mechanical engineer" in ans
    assert "cad" in ans or "thermodynamics" in ans or "manufacturing" in ans or "solidworks" in ans

def test_test3_doctor_after_12th():
    """TEST 3: 'I want to become a doctor. What should I do after 12th?' -> Medicine-specific pathway."""
    session_id = f"test-doc-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I want to become a doctor. What should I do after 12th?")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "doctor" in ans or "mbbs" in ans or "medicine" in ans
    assert "neet" in ans or "biology" in ans or "clinical" in ans or "internship" in ans

def test_test4_lawyer():
    """TEST 4: 'I want to become a lawyer.' -> Law-specific guidance."""
    session_id = f"test-law-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I want to become a lawyer.")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "lawyer" in ans or "law" in ans or "llb" in ans
    assert "clat" in ans or "bar" in ans or "litigation" in ans or "court" in ans

def test_test5_teacher():
    """TEST 5: 'I want to become a teacher.' -> Teaching-specific guidance."""
    session_id = f"test-teach-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I want to become a teacher.")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "teacher" in ans or "teaching" in ans or "educator" in ans
    assert "b.ed" in ans or "pedagogy" in ans or "tet" in ans or "classroom" in ans

def test_test6_graphic_designer():
    """TEST 6: 'I want to become a graphic designer.' -> Design-specific guidance."""
    session_id = f"test-design-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I want to become a graphic designer.")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "graphic design" in ans or "designer" in ans
    assert "portfolio" in ans or "figma" in ans or "illustrator" in ans or "photoshop" in ans

def test_test7_finance():
    """TEST 7: 'I want to work in finance.' -> Finance-specific guidance."""
    session_id = f"test-fin-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I want to work in finance.")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "finance" in ans or "banking" in ans or "financial" in ans
    assert "excel" in ans or "valuation" in ans or "ca" in ans or "cfa" in ans or "accounting" in ans

def test_test8_government_jobs():
    """TEST 8: 'I want to prepare for government jobs.' -> Government-job-specific guidance."""
    session_id = f"test-gov-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I want to prepare for government jobs.")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "government" in ans or "civil services" in ans or "upsc" in ans or "ssc" in ans
    assert "general studies" in ans or "aptitude" in ans or "exam" in ans

def test_test9_employability_skills():
    """TEST 9: 'What are employability skills?' -> General career guidance."""
    session_id = f"test-emp-{uuid.uuid4()}"
    res = process_chat_message(session_id, "What are employability skills?")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "employability skills" in ans
    assert "communication" in ans and "problem-solving" in ans

def test_test10_what_skills_should_i_learn_no_context():
    """
    TEST 10: 'What skills should I learn?'
    When no career is provided, assistant must prompt for career context
    rather than automatically assuming Python/AI.
    """
    session_id = f"test-skills-none-{uuid.uuid4()}"
    res = process_chat_message(session_id, "What skills should I learn?")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    # Must explain that skills depend on career path and ask user for field
    assert "depend" in ans or "target profession" in ans or "what career" in ans or "field of study" in ans
    # Must NOT say "Stage 1: Foundations (Start Here!) Python" without context!
    assert "stage 1: foundations (start here!)" not in ans

def test_test11_civil_engineering_internship_follow_up():
    """
    TEST 11:
    Turn 1: 'I want to become a civil engineer.'
    Turn 2: 'What internships should I do?'
    -> Civil Engineering internships, NOT software internships.
    """
    session_id = f"test-turn-civil-{uuid.uuid4()}"
    r1 = process_chat_message(session_id, "I want to become a civil engineer.")
    assert r1["status_code"] == 200

    r2 = process_chat_message(session_id, "What internships should I do?")
    assert r2["status_code"] == 200
    ans = r2["response"].lower()
    assert "civil" in ans
    assert "construction" in ans or "site" in ans or "structural" in ans or "surveying" in ans
    assert "software internship" not in ans

def test_test12_mechanical_engineering_mock_interview():
    """
    TEST 12:
    Turn 1: 'I want to become a mechanical engineer.'
    Turn 2: 'Take my mock interview.'
    -> Mechanical Engineering mock interview with mechanical questions.
    """
    session_id = f"test-turn-mech-{uuid.uuid4()}"
    r1 = process_chat_message(session_id, "I want to become a mechanical engineer.")
    assert r1["status_code"] == 200

    r2 = process_chat_message(session_id, "Take my mock interview.")
    assert r2["status_code"] == 200
    ans = r2["response"].lower()
    assert "mock interview" in ans
    assert "mechanical" in ans
    # Must contain mechanical-relevant question terms
    assert "mechanical" in ans or "cad" in ans or "thermodynamic" in ans or "design" in ans

def test_test13_hindi_multilingual():
    """TEST 13 (Multilingual): 'Mujhe civil engineer banna hai' -> Civil Engineering detected."""
    session_id = f"test-hindi-{uuid.uuid4()}"
    res = process_chat_message(session_id, "Mujhe civil engineer banna hai")
    assert res["status_code"] == 200
    ctx = memory_store.get_user_context(session_id)
    assert "civil" in ctx["career_interest"].lower()

def test_test14_gujarati_multilingual():
    """TEST 14 (Multilingual): 'Hu mechanical engineer banva maangu chu' -> Mechanical Engineering detected."""
    session_id = f"test-guj-{uuid.uuid4()}"
    res = process_chat_message(session_id, "Hu mechanical engineer banva maangu chu")
    assert res["status_code"] == 200
    ctx = memory_store.get_user_context(session_id)
    assert "mechanical" in ctx["career_interest"].lower()

def test_session_reset():
    """Verifies that reset_session clears memory and profile data."""
    session_id = f"test-reset-{uuid.uuid4()}"
    process_chat_message(session_id, "I am a civil engineering student.")
    ctx_before = memory_store.get_user_context(session_id)
    assert ctx_before["field"] != ""

    memory_store.reset_session(session_id)
    ctx_after = memory_store.get_user_context(session_id)
    assert ctx_after["field"] == ""
    assert ctx_after["skills"] == []

    messages = memory_store.get_recent_messages(session_id)
    assert len(messages) == 0

def test_pharmacy_roadmap_exact_query():
    """
    TEST: 'explain roadmap in pharmacy'
    Must NOT return the Welcome to CareerBridge AI screen.
    Must return actual pharmacy roadmap covering education (B.Pharm/D.Pharm), subjects, lab skills, internships, licensing.
    """
    session_id = f"test-pharm-exact-{uuid.uuid4()}"
    res = process_chat_message(session_id, "explain roadmap in pharmacy")
    assert res["status_code"] == 200
    ans = res["response"]
    ans_lower = ans.lower()
    # Must NOT be welcome screen
    assert "welcome to careerbridge ai" not in ans_lower
    # Must be pharmacy specific
    assert "pharmacy" in ans_lower
    assert "pharm" in ans_lower
    assert any(w in ans_lower for w in ["b.pharm", "d.pharm", "pharmacology", "pharmaceutics", "licensing", "chemist"])

def test_pharmacy_conversational_context():
    """
    TEST Multi-turn Context for Pharmacy:
    Turn 1: 'I want to become a pharmacist.' -> Pharmacy guidance
    Turn 2: 'What skills should I learn?' -> Pharmacy skills
    Turn 3: 'What internships should I look for?' -> Pharmacy internships
    Turn 4: 'Take my mock interview.' -> Pharmacy interview questions
    """
    session_id = f"test-pharm-turns-{uuid.uuid4()}"
    r1 = process_chat_message(session_id, "I want to become a pharmacist.")
    assert r1["status_code"] == 200
    assert "pharm" in r1["response"].lower()
    assert "welcome to careerbridge ai" not in r1["response"].lower()

    r2 = process_chat_message(session_id, "What skills should I learn?")
    assert r2["status_code"] == 200
    assert "pharm" in r2["response"].lower()
    assert any(s in r2["response"].lower() for s in ["pharmacology", "formulation", "therapeutics", "dispensing", "analysis"])

    r3 = process_chat_message(session_id, "What internships should I look for?")
    assert r3["status_code"] == 200
    assert "pharm" in r3["response"].lower()
    assert any(i in r3["response"].lower() for i in ["hospital", "manufacturing", "retail", "clinical"])

    r4 = process_chat_message(session_id, "Take my mock interview.")
    assert r4["status_code"] == 200
    assert "mock interview" in r4["response"].lower()
    assert "pharm" in r4["response"].lower() or "drug" in r4["response"].lower() or "prescription" in r4["response"].lower()

def test_first_interview_preparation():
    """TEST: 'How do I prepare for my first interview?' -> General interview guidance, never welcome screen."""
    session_id = f"test-first-interview-{uuid.uuid4()}"
    res = process_chat_message(session_id, "How do I prepare for my first interview?")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "welcome to careerbridge ai" not in ans
    assert "star" in ans or "interview" in ans
    assert "research" in ans or "questions" in ans

def test_career_context_switch():
    """
    TEST: Career Context Switching
    Session starts with Civil Engineering, then switches to Pharmacy.
    Subsequent questions must follow Pharmacy.
    """
    session_id = f"test-switch-{uuid.uuid4()}"
    # Start with Civil
    r1 = process_chat_message(session_id, "I want to become a civil engineer.")
    assert "civil" in r1["response"].lower()

    # Follow-up on Civil
    r2 = process_chat_message(session_id, "What skills should I learn?")
    assert "civil" in r2["response"].lower()
    assert "autocad" in r2["response"].lower() or "staad" in r2["response"].lower()

    # Switch to Pharmacy
    r3 = process_chat_message(session_id, "I want to become a pharmacist.")
    assert "pharm" in r3["response"].lower()

    # Subsequent follow-up should now be Pharmacy
    r4 = process_chat_message(session_id, "What skills should I learn?")
    assert "pharm" in r4["response"].lower()
    assert "civil" not in r4["response"].lower()

def test_btech_cse_roadmap():
    """
    TEST: 'I am a B.Tech CSE student. Give me a 4-year roadmap.'
    Must return comprehensive 4-year B.Tech CSE roadmap with DSA, Core CS, Projects, and Placements.
    """
    session_id = f"test-btech-cse-{uuid.uuid4()}"
    res = process_chat_message(session_id, "I am a B.Tech CSE student. Give me a 4-year roadmap.")
    assert res["status_code"] == 200
    ans = res["response"].lower()
    assert "b.tech" in ans and "cse" in ans
    assert "dsa" in ans or "data structures" in ans
    assert "operating systems" in ans or "dbms" in ans or "git" in ans
    # Check that context recognized B.Tech CSE
    ctx = memory_store.get_user_context(session_id)
    assert "cse" in ctx["field"].lower() or "cse" in ctx["career_interest"].lower()

def test_btech_cse_follow_ups():
    """
    TEST: Multi-turn conversational context for B.Tech CSE:
    Turn 1: 'I am pursuing B.Tech in CSE.'
    Turn 2: 'What skills should I learn?' -> DSA, OS, DBMS, Networks, Full-stack
    Turn 3: 'What internships should I do?' -> SDE internships, GSoC, Open-source
    Turn 4: 'Take my mock interview.' -> CSE technical questions
    """
    session_id = f"test-cse-turns-{uuid.uuid4()}"
    r1 = process_chat_message(session_id, "I am pursuing B.Tech in CSE.")
    assert r1["status_code"] == 200
    assert "b.tech" in r1["response"].lower() or "cse" in r1["response"].lower()

    r2 = process_chat_message(session_id, "What skills should I learn?")
    assert r2["status_code"] == 200
    assert any(w in r2["response"].lower() for w in ["dsa", "algorithms", "operating systems", "dbms"])

    r3 = process_chat_message(session_id, "What internships should I do?")
    assert r3["status_code"] == 200
    assert any(w in r3["response"].lower() for w in ["sde", "software", "open-source", "gsoc", "git"])

    r4 = process_chat_message(session_id, "Take my mock interview.")
    assert r4["status_code"] == 200
    assert "mock interview" in r4["response"].lower()
    assert any(w in r4["response"].lower() for w in ["complexity", "quicksort", "database", "http", "process", "thread", "oop"])

