import os
import json
import traceback

def handler(request):
    try:
        # Lazy imports for C extensions
        import bcrypt
        from supabase import create_client, Client
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to import modules",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Environment variables
    try:
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        if not SUPABASE_URL or not SUPABASE_KEY:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Supabase credentials missing"})
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error reading environment variables",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to initialize Supabase client",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Only accept POST requests
    try:
        if request.method != "POST":
            return {
                "statusCode": 405,
                "body": json.dumps({"message": f"Method {request.method} not allowed"})
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error checking HTTP method",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Parse JSON body safely (Vercel-compatible)
    try:
        data = request.json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing username or password"})
            }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid JSON request body",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Query Supabase
    try:
        response = supabase.table("users").select("*").eq("username", username).execute()
        user_data = response.data if hasattr(response, "data") else response.get("data")

        if not user_data:
            return {"statusCode": 401, "body": json.dumps({"message": "Invalid credentials"})}

        user = user_data[0]
        hashed_password = user.get("password")
        if not hashed_password:
            return {"statusCode": 500, "body": json.dumps({"message": "Stored password missing"})}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error querying Supabase",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Verify password
    try:
        if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            return {"statusCode": 200, "body": json.dumps({"message": "Login successful"})}
        else:
            return {"statusCode": 401, "body": json.dumps({"message": "Invalid credentials"})}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error verifying password",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }
