"""
Quick test script for Phase 2 semantic matching
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from utils.semantic_utils import analyze_resume_jd_match

# Test data
resume_text = """
Sarah Johnson - Software Engineer

EXPERIENCE:
Senior Software Engineer at TechCorp (2021-Present)
- Developed REST APIs using Python and FastAPI framework
- Built microservices architecture with Docker and Kubernetes  
- Worked with PostgreSQL and MongoDB databases
- Led a team of 3 junior developers in Agile/Scrum environment

SKILLS:
Python, FastAPI, Docker, Kubernetes, PostgreSQL, MongoDB, Git, Agile
"""

jd_text = """
Software Engineer Position

We are seeking a talented Software Engineer to join our backend team.

REQUIREMENTS:
- 2+ years of experience in software development
- Strong proficiency in Python
- Experience with FastAPI or Flask framework
- Knowledge of REST API design and implementation
- Familiarity with SQL and NoSQL databases (PostgreSQL, MongoDB)
- Experience with containerization (Docker)
- Understanding of Agile methodologies
"""

print("🧪 Testing Phase 2 Semantic Matching...\n")
print("=" * 60)

try:
    result = analyze_resume_jd_match(resume_text, jd_text)
    
    print(f"\n✅ Analysis Complete!\n")
    print(f"📊 Match Score: {result['match_score']}%")
    
    print(f"\n✅ Strengths ({len(result['strengths'])}):")
    for i, strength in enumerate(result['strengths'], 1):
        print(f"  {i}. {strength}")
    
    print(f"\n⚠️  Gaps ({len(result['gaps'])}):")
    for i, gap in enumerate(result['gaps'], 1):
        print(f"  {i}. {gap}")
    
    print("\n" + "=" * 60)
    print("🎉 Phase 2 semantic matching is working successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
