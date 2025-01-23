import base64
import binascii
import datetime
import re


def log_event(event):
    print(f"Configuration: File name: {event['name']}")
    print(f"Configuration: Bucket Name: {event['bucket']}")


def md5hash_to_md5sum(md5hash):
    decode_hash = base64.b64decode(md5hash)
    encoded_hash = binascii.hexlify(decode_hash)
    return str(encoded_hash, "utf-8")


def get_questionnaire_name(zip_filename):
    match = re.search(r"^([a-zA-Z]+)(\d{4})([a-zA-Z]*)(?:edit)?\.zip", zip_filename)
    if match:
        survey, year_month, survey_version = match.groups()
        questionnaire_name = survey + year_month + survey_version
        return f"{questionnaire_name}"
    else:
        return None

class InvalidFileExtension(Exception):
    pass


class InvalidFileType(Exception):
    pass
