from supabase import create_client, Client
import bcrypt
import json

import os
url = os.environ.get("https://vjnzkzoaxtkqhtsaaxzl.supabase.co")
key = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZqbnprem9heHRrcWh0c2FheHpsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTk1Mzg1NywiZXhwIjoyMDc1NTI5ODU3fQ.ZKfkTYHbyYB51b77PtVfVdv5RmAKRpJ17z-QqxaKuPY")
supabase: Client = create_client(url, key)

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"message": "Method not allowed"}),
        }

    try:
        body = request.body.decode()
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing fields"}),
            }

        response = supabase.table("users").select("*").eq("username", username).execute()
        if not response.data:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "Username not found"}),
            }

        user = response.data[0]
        hashed_password = user["password"]

        if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Login successful"}),
            }
        else:
            return {
                "statusCode": 401,
                "body": json.dumps({"message": "Incorrect password"}),
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Server error: {str(e)}"}),
        }
