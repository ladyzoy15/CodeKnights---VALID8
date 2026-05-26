
import os

log_path = "backend_error.txt"
if os.path.exists(log_path):
    with open(log_path, "rb") as f:
        content = f.read()
    
    # Try different encodings
    for enc in ["utf-16", "utf-8", "latin-1"]:
        try:
            text = content.decode(enc)
            print(f"--- Decoded with {enc} ---")
            for line in text.splitlines():
                if "email" in line.lower() or "student" in line.lower() or "fail" in line.lower():
                    print(line)
            break
        except Exception:
            continue
else:
    print("Log file not found.")
