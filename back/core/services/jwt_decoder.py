import base64
import hmac
import json
from django.conf import settings
from datetime import datetime, timedelta


class AbyssJwtValidator:
    _ABYSS_ALGORITHM = 'sha256'
    _ABYSS_SECRET_KEY = settings.ABYSS_JWT_KEY.encode()

    def __init__(self, jwt_key):
        jwt_parts = jwt_key.split('.')
        # Params
        self._valid = False
        self._data = None
        if len(jwt_parts) == 3:
            self._header, self._payload, self._income_signature = jwt_parts
            if self._validate():
                self._valid = True
                self._data = self._get_data()

    @property
    def valid(self):
        return self._valid

    @property
    def data(self):
        return self._data

    def _get_data(self):
        _data = self._decode_str_with_fix_padding(self._payload)
        return json.loads(_data)

    def _validate(self):
        income_sig = self._decode_str_with_fix_padding(self._income_signature)
        check_sig = self._create_check_signature()
        if income_sig != check_sig:
            return False
        payload_dict = self._get_data()
        try:
            # created_date = payload_dict['timestamp']
            created_date = 1605790124.049204    # TODO: REMOVE AFTER TESTS
        except KeyError:
            return False

        check_date = datetime.timestamp(datetime.now()) - 86400
        if created_date > check_date:
            self._data = payload_dict
            return True
        return False

    @staticmethod
    def _decode_str_with_fix_padding(value: str):
        val = value.encode()
        try:
            return_val = base64.urlsafe_b64decode(val)
        except ValueError:
            val += b"=" * ((4 - len(val) % 4) % 4)
            return_val = base64.urlsafe_b64decode(val)
        return return_val

    def _create_check_signature(self):
        msg = f'{self._header}.{self._payload}'.encode()
        context = hmac.new(self._ABYSS_SECRET_KEY, msg, self._ABYSS_ALGORITHM)
        return context.digest()
