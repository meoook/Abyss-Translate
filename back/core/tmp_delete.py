import base64


def decode_with_fix_padding(value: str):
    val = value.encode()
    try:
        return_val = base64.urlsafe_b64decode(val)
    except ValueError:
        print('FIXED')
        val += b"=" * ((4 - len(val) % 4) % 4)
        return_val = base64.urlsafe_b64decode(val)
    print(return_val)
    return return_val


def jwt_decode(jwt: str):
    SECRET_KEY = 'cAtwa1kkEy'
    print('JWT IS', jwt)
    jwt_parts = jwt.split('.')
    if len(jwt_parts) != 3:
        return False
    # try:
    header = decode_with_fix_padding(jwt_parts[0])
    payload = decode_with_fix_padding(jwt_parts[1])
    signature = decode_with_fix_padding(jwt_parts[2])
    print('HEADER IS', header)
    print('PAYLOAD IS', payload)
    print('SIGNATURE IS', signature)
    print(signature.decode(errors='ignore'))

    return True


if __name__ == '__main__':
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ4YXhzYWFzYXNkIiwibmFtZSI6ImFzYXNkZiIsImlhdCI6MTUxNjIzOTAyMn0.C0UmT56z69HZmEn72C1lkSgwBC8FTY1Y6BSRXPiDf-A'
    jwt_decode(token)
