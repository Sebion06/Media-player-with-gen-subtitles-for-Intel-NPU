from googletrans import Translator
import googletrans


def get_translator():
    return Translator()


def get_languages():
    return googletrans.LANGUAGES


def translate_text(text, src, dest):
    try:
        translator = Translator()
        translation = translator.translate(text=text, src=src, dest=dest)
        return translation.text
    except TypeError:
        return None


def start_live_translation(old_subtitles, translated_subtitles, output_language):
    for item in old_subtitles:
        item = list(item)
        item[2] = translate_text(
            item[2], "en", output_language)
        translation = tuple(item)
        translated_subtitles.append(translation)