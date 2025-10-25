import os
import json
import traceback

def handler(request):
    # Lazy imports for C extensions
    try:
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

    # Debug: environment variables
    try:
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        print("DEBUG: SUPABASE_URL =", SUPABASE_URL)
        print("DEBUG: SUPABASE_KEY =", "[HIDDEN]" if SUPABASE_KEY else None)

        if not SUPABASE_URL or not SUPABASE_KEY:
            return {"statusCode": 500, "body": json.dumps({"message": "Supabase credentials missing"})}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error checking environment variables",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("DEBUG: Supabase client initialized")
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to initialize Supabase client",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Ensure POST request
    try:
        if request.method != "POST":
            print("DEBUG: Invalid method:", request.method)
            return {"statusCode": 405, "body": json.dumps({"message": "Method not allowed"})}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error checking HTTP method",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Parse request body
    try:
        body = request.body.decode()
        print("DEBUG: Raw request body:", body)
        data = json.loads(body)
        username = data.get("username")
        password = data.get("password")
        print("DEBUG: username =", username)
        print("DEBUG: password =", "[HIDDEN]" if password else None)

        if not username or not password:
            return {"statusCode": 400, "body": json.dumps({"message": "Missing fields"})}
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error parsing request body",
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }

    # Query Supabase
    try:
        response = supabase.table("users").select("*").eq("username", username).execute()
        print("DEBUG: Supabase response:", response)
        user_data = response.data if hasattr(response, "data") else response.get("data")
        if not user_data:
            return {"statusCode": 401, "body": json.dumps({"message": "Invalid credentials"})}
        user = user_data[0]
        hashed_password = user.get("password")
        print("DEBUG: hashed_password =", hashed_password)
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
            print("DEBUG: Password match")
            return {"statusCode": 200, "body": json.dumps({"message": "Login successful"})}
        else:
            print("DEBUG: Password mismatch")
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
