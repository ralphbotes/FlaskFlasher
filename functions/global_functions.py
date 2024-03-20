from datetime import datetime

def get_current_datetime_str():
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return current_datetime_str

def clean(text):
    new_text = ""
    characters_to_remove = ",[]()'"

    for char in text:
        if char not in characters_to_remove:
            new_text += char

    return new_text