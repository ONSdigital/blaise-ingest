import re


def log_event(event):
    print(f"Configuration: File name: {event['name']}")
    print(f"Configuration: Bucket Name: {event['bucket']}")


def get_questionnaire_name(zip_filename):
    match = re.search(r"(?i)^([a-zA-Z]+)(\d{4})([a-zA-Z]?).*\.zip", zip_filename)
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
