
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
os.environ["SECRET_KEY"] = "secret"
os.environ["REDIS_URL"] = "redis://localhost"

try:
    print("Step 1: Importing app.services.email_service")
    from app.services.email_service import EmailDeliveryError
    print("Step 1 SUCCESS")
    
    print("Step 2: Importing app.routers.users")
    import app.routers.users as users_router
    print(f"Step 2 SUCCESS. users_router has EmailDeliveryError: {hasattr(users_router, 'EmailDeliveryError')}")
    
    print("Step 3: Importing app.main")
    from app.main import app
    print("Step 3 SUCCESS")
    
    print("FINAL VERIFICATION")
    routes = [route.path for route in app.routes]
    critical_routes = ["/auth/google", "/api/school/admin/create-school-it", "/api/users/students/"]
    for cr in critical_routes:
        exists = any(cr in r for r in routes)
        print(f"{'VERIFIED' if exists else 'MISSING'}: {cr}")

except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
