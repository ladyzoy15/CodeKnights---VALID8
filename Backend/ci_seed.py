import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

repo_root = Path(__file__).resolve().parent.parent
backend_path = repo_root / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.role import Role
from app.models.school import School
from app.models.department import Department
from app.models.program import Program
from modules.core import wipe_records, seed_roles, seed_permission_catalog, seed_attendance_methods, seed_attendance_statuses, seed_event_types

def seed_ci_users():
    db = SessionLocal()
    try:
        seed_roles(db)
        seed_permission_catalog(db)
        seed_attendance_methods(db)
        seed_attendance_statuses(db)
        seed_event_types(db)
        
        # Create a school
        school = db.query(School).filter_by(school_code="TEST-001").first()
        if not school:
            school = School(
                legal_name="Test University", 
                display_name="Test University", 
                school_code="TEST-001", 
                address="CI Test Address",
                is_active=True
            )
            db.add(school)
            db.flush()
            
        # Create department & program
        dept = db.query(Department).filter_by(school_id=school.id).first()
        if not dept:
            dept = Department(school_id=school.id, name="CI Department")
            db.add(dept)
            db.flush()
            
        prog = db.query(Program).filter_by(school_id=school.id).first()
        if not prog:
            prog = Program(school_id=school.id, name="CI Program")
            db.add(prog)
            db.flush()

        roles = {r.code: r for r in db.query(Role).all()}
        
        users_to_create = [
            ("campus_admin@test.com", "TestPass123!", "campus_admin", "Campus", "Admin"),
            ("student@test.com", "TestPass123!", "student", "Normal", "Student"),
        ]
        
        from app.models.user import StudentProfile
        
        for email, pwd, role_code, fname, lname in users_to_create:
            user = db.query(User).filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    school_id=school.id,
                    first_name=fname,
                    last_name=lname,
                    is_active=True,
                    must_change_password=False
                )
                user.set_password(pwd)
                db.add(user)
                db.flush()
                
                if role_code == "student":
                    profile = StudentProfile(
                        user_id=user.id,
                        school_id=school.id,
                        student_number=f"CI-{user.id}",
                        department_id=dept.id,
                        program_id=prog.id,
                        year_level=1
                    )
                    db.add(profile)
                
            role = roles.get(role_code)
            if role:
                ur = db.query(UserRole).filter_by(user_id=user.id, role_id=role.id).first()
                if not ur:
                    db.add(UserRole(user_id=user.id, role_id=role.id))
                    
        db.commit()
        print("Successfully seeded CI users.")
    except Exception as e:
        db.rollback()
        print(f"Failed to seed CI users: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_ci_users()
