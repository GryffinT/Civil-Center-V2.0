import os
import json
import bcrypt
from supabase import create_client, Client

# -----------------------------
# Supabase Client Setup
# -----------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Login Handler
# -----------------------------
def handler(request):
    if request.method != "POST":
        return {"statusCode": 405, "body": json.dumps({"message": "Method not allowed"})}

    try:
        body = request.body.decode() 
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"statusCode": 400, "body": json.dumps({"message": "Missing fields"})}

        response = supabase.table("users").select("*").eq("username", username).execute()
        user_data = response.data if hasattr(response, "data") else response.get("data")

        if not user_data:
            return {"statusCode": 401, "body": json.dumps({"message": "Invalid credentials"})}

        user = user_data[0]
        hashed_password = user.get("password")
        if not hashed_password:
            return {"statusCode": 500, "body": json.dumps({"message": "Stored password missing"})}

        if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            return {"statusCode": 200, "body": json.dumps({"message": "Login successful"})}
        else:
            return {"statusCode": 401, "body": json.dumps({"message": "Invalid credentials"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": f"Server error: {str(e)}"})}
