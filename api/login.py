def handler(request):
    print("Function executed!")
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": "Hello world"
    }
