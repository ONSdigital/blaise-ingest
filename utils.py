import re


def log_event(event):
    print(f"Configuration: File name: {event['name']}")
    print(f"Configuration: Bucket Name: {event['bucket']}")


def get_questionnaire_name(zip_filename):
    match = re.search(r"^(.*?)(?=\.zip$)", zip_filename)
    if match:
        # Only get the first group (everything before ".zip")
        questionnaire_name = match.group(1)
        return f"{questionnaire_name}"
    else:
        return None


class InvalidFileExtension(Exception):
    pass


class InvalidFileType(Exception):
    pass
