def success_response(data=None, message="Operation successful"):
    return {
        "status": "success",
        "message": message,
        "data": data
    }

def error_response(message="An error occurred", status_code=400):
    return {
        "status": "error",
        "message": message,
        "status_code": status_code
    }