"""Internationalization package — supports English, Thai, and Myanmar."""

from bot.i18n.en import STRINGS as EN_STRINGS
from bot.i18n.th import STRINGS as TH_STRINGS
from bot.i18n.my import STRINGS as MY_STRINGS

_LANGUAGES = {
    "en": EN_STRINGS,
    "th": TH_STRINGS,
    "my": MY_STRINGS,
}

LANGUAGE_NAMES = {
    "en": "English",
    "th": "ไทย",
    "my": "မြန်မာ",
}


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """Get a translated string by key and language code.
    
    Falls back to English if the key is not found in the target language.
    Supports .format()-style kwargs for interpolation.
    """
    strings = _LANGUAGES.get(lang, EN_STRINGS)
    text = strings.get(key, EN_STRINGS.get(key, f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
