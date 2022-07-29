from fastapi_microsoft_identity import AuthError, validate_scope

def check_expected_scope(request):
    return_code = 200
    try:
        validate_scope("profile.read", request)
    except AuthError as auth_err:
        return_code = auth_err.status_code
    return return_code
