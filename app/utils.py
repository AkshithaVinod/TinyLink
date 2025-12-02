import shortuuid

def generate_short_code() -> str:
    return shortuuid.uuid()[:8]
