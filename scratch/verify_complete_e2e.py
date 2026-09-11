"""
End-to-End Live Verification Script for CareerBridge AI Chatbot Bug Fix
Tests all conditions required by the user prompt via HTTP requests to http://127.0.0.1:8000
"""
import sys
import uuid
import httpx

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000"

def run_test(name, fn):
    print(f"\n==================================================")
    print(f"RUNNING: {name}")
    print(f"==================================================")
    try:
        fn()
        print(f"PASS: {name}")
        return True
    except AssertionError as ae:
        print(f"FAIL: {name} - {ae}")
        return False
    except Exception as e:
        print(f"ERROR: {name} - {e}")
        return False

def test_exact_pharmacy_roadmap():
    session_id = f"pharm-exact-{uuid.uuid4()}"
    with httpx.Client(timeout=10.0) as client:
        res = client.post(f"{BASE_URL}/chat", json={"message": "explain roadmap in pharmacy", "session_id": session_id})
        assert res.status_code == 200, f"Status code {res.status_code}"
        data = res.json()
        response = data["response"]
        print(f"[Query]: explain roadmap in pharmacy")
        print(f"[Response Snippet]:\n{response[:350]}...\n")
        
        # Verify it NEVER returns the welcome screen
        assert "welcome to careerbridge ai" not in response.lower(), "Returned Welcome screen instead of answer!"
        # Verify it is Pharmacy specific
        assert "pharmacy" in response.lower() or "pharmacist" in response.lower()
        assert any(term in response.lower() for term in ["b.pharm", "d.pharm", "pharmacology", "pharmaceutics", "licensing"])

def test_pharmacy_multi_turn_context():
    session_id = f"pharm-context-{uuid.uuid4()}"
    with httpx.Client(timeout=10.0) as client:
        # Turn 1
        r1 = client.post(f"{BASE_URL}/chat", json={"message": "I want to become a pharmacist.", "session_id": session_id}).json()["response"]
        print(f"Turn 1 (Become Pharmacist):\n{r1[:180]}...\n")
        assert "pharm" in r1.lower()
        assert "welcome to careerbridge ai" not in r1.lower()
        
        # Turn 2: What skills should I learn?
        r2 = client.post(f"{BASE_URL}/chat", json={"message": "What skills should I learn?", "session_id": session_id}).json()["response"]
        print(f"Turn 2 (Skills):\n{r2[:180]}...\n")
        assert "pharm" in r2.lower()
        assert any(s in r2.lower() for s in ["pharmacology", "formulation", "therapeutics", "dispensing", "analysis"])
        
        # Turn 3: What internships should I look for?
        r3 = client.post(f"{BASE_URL}/chat", json={"message": "What internships should I look for?", "session_id": session_id}).json()["response"]
        print(f"Turn 3 (Internships):\n{r3[:180]}...\n")
        assert "pharm" in r3.lower()
        assert any(i in r3.lower() for i in ["hospital", "manufacturing", "retail", "clinical"])
        
        # Turn 4: Take my mock interview.
        r4 = client.post(f"{BASE_URL}/chat", json={"message": "Take my mock interview.", "session_id": session_id}).json()["response"]
        print(f"Turn 4 (Mock Interview):\n{r4[:180]}...\n")
        assert "mock interview" in r4.lower()
        assert "pharm" in r4.lower() or "drug" in r4.lower() or "prescription" in r4.lower()

def test_multiple_professions():
    queries = [
        ("I want to become a civil engineer. Explain the roadmap.", ["civil engineering", "autocad", "staad"]),
        ("I want to become a pharmacist. Explain the roadmap.", ["pharmacy", "pharmacology", "b.pharm"]),
        ("I want to become a mechanical engineer.", ["mechanical", "cad", "thermodynamics"]),
        ("I want to become a lawyer.", ["law", "clat", "bar"]),
        ("I want to become a teacher.", ["teacher", "teaching", "b.ed"]),
        ("I want to become a graphic designer.", ["graphic design", "figma", "illustrator"]),
        ("I want to work in finance.", ["finance", "banking", "financial"]),
        ("I want to become a doctor.", ["doctor", "mbbs", "medicine"]),
        ("What are employability skills?", ["employability skills", "communication", "problem-solving"]),
        ("How do I prepare for my first interview?", ["star", "interview", "research"])
    ]
    with httpx.Client(timeout=10.0) as client:
        for q, expected_terms in queries:
            sid = f"prof-{uuid.uuid4()}"
            res = client.post(f"{BASE_URL}/chat", json={"message": q, "session_id": sid}).json()["response"]
            print(f"[Query]: {q}")
            print(f"[Answer]: {res.splitlines()[0]}")
            assert "welcome to careerbridge ai" not in res.lower(), f"Returned welcome screen for query: {q}"
            assert any(t in res.lower() for t in expected_terms), f"Expected terms {expected_terms} not found in {res[:150]}"

def test_context_switching_flow():
    session_id = f"switch-{uuid.uuid4()}"
    with httpx.Client(timeout=10.0) as client:
        # Start Civil
        r1 = client.post(f"{BASE_URL}/chat", json={"message": "I want to become a civil engineer.", "session_id": session_id}).json()["response"]
        assert "civil" in r1.lower()
        
        # Follow up 1: skills
        r2 = client.post(f"{BASE_URL}/chat", json={"message": "What skills should I learn?", "session_id": session_id}).json()["response"]
        assert "civil" in r2.lower()
        
        # Follow up 2: internships
        r3 = client.post(f"{BASE_URL}/chat", json={"message": "What internships should I do?", "session_id": session_id}).json()["response"]
        assert "civil" in r3.lower()
        
        # Follow up 3: mock interview
        r4 = client.post(f"{BASE_URL}/chat", json={"message": "Now take my interview.", "session_id": session_id}).json()["response"]
        assert "civil" in r4.lower()
        assert "mock interview" in r4.lower()
        
        # Switch to Pharmacy
        r5 = client.post(f"{BASE_URL}/chat", json={"message": "I want to become a pharmacist.", "session_id": session_id}).json()["response"]
        assert "pharm" in r5.lower()
        
        # Follow up in new context: skills should be pharmacy
        r6 = client.post(f"{BASE_URL}/chat", json={"message": "What skills should I learn?", "session_id": session_id}).json()["response"]
        assert "pharm" in r6.lower()
        assert "civil" not in r6.lower()

def test_out_of_scope_geography():
    session_id = f"oos-{uuid.uuid4()}"
    with httpx.Client(timeout=10.0) as client:
        res = client.post(f"{BASE_URL}/chat", json={"message": "What is the capital of France?", "session_id": session_id}).json()["response"]
        print(f"[Out of Scope Query]: What is the capital of France?")
        print(f"[Response]:\n{res}\n")
        assert "welcome to careerbridge ai" not in res.lower()
        assert "career" in res.lower() or "employability" in res.lower()
        assert "only support ai" not in res.lower()

if __name__ == "__main__":
    results = [
        run_test("1. Exact Pharmacy Roadmap ('explain roadmap in pharmacy')", test_exact_pharmacy_roadmap),
        run_test("2. Pharmacy Multi-Turn Conversational Context", test_pharmacy_multi_turn_context),
        run_test("3. Multiple Professions Test (10 scenarios)", test_multiple_professions),
        run_test("4. Context Switching Flow (Civil -> Pharmacy)", test_context_switching_flow),
        run_test("5. Out-of-Scope Redirection ('capital of France')", test_out_of_scope_geography),
    ]
    if all(results):
        print("\nALL 5 COMPREHENSIVE E2E TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED!")
        sys.exit(1)
