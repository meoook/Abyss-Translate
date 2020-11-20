import base64
import hmac

SECRET_FROM_DJANGO_SETTINGS = '46c1d9292aee91cf7f091a1121879a6bf35cc459bcb0ed8a9a52d8d9c0f2bc83'


def decode_with_fix_padding(value: str):
    val = value.encode()
    try:
        return_val = base64.urlsafe_b64decode(val)
    except ValueError:
        val += b"=" * ((4 - len(val) % 4) % 4)
        return_val = base64.urlsafe_b64decode(val)
    return return_val


def create_signature(header_part, payload_part):
    algorithm = 'sha256'
    secret_binary = SECRET_FROM_DJANGO_SETTINGS.encode()
    msg = f'{header_part}.{payload_part}'.encode()
    context = hmac.new(secret_binary, msg, algorithm)
    return context


def jwt_decode(jwt: str):
    jwt_parts = jwt.split('.')
    if len(jwt_parts) != 3:
        return False
    # try:
    header = decode_with_fix_padding(jwt_parts[0])
    payload = decode_with_fix_padding(jwt_parts[1])
    print('HEADER IS', header)
    print('PAYLOAD IS', payload)
    signature = create_signature(jwt_parts[0], jwt_parts[1])
    print('SIGNATURE IS', signature)
    print(signature.digest())
    print(decode_with_fix_padding(jwt_parts[2]))

    return True


if __name__ == '__main__':
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiMDA3Yi1lZWNmLTM3MDAtMDE4OCIsIm5pY2tuYW1lIjoiUGFSWjFWQUwiLCJ0YWciOiIwMDExIiwibGFuZyI6ImVuIn0.GOZQAecsqU6-PfEFG8jIOZfBmRzM1ww3V4MNmDsQrd4'
    jwt_decode(token)
