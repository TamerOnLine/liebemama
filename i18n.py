import os
import re
import subprocess
from pathlib import Path
from deep_translator import GoogleTranslator

# ----------- Manual settings here ----------
LANGUAGES = ["ar", "de"]
BABEL_CFG = "babel.cfg"
POT_FILE = "messages.pot"
OUTPUT_DIR = "translations"
# ------------------------------------------

def fix_placeholders(msgid, translated):
    """
    Ensure translation retains placeholders present in the original message ID.

    Args:
        msgid (str): Original message string with placeholders.
        translated (str): Translated string that may need placeholder correction.

    Returns:
        str: Corrected translated string including necessary placeholders.
    """
    patterns = [
        re.compile(r"%\([^)]+\)s"),   # e.g., %(name)s
        re.compile(r"\{[^}]+\}")      # e.g., {default}
    ]
    for pattern in patterns:
        placeholders = pattern.findall(msgid)
        for ph in placeholders:
            if ph not in translated:
                translated = re.sub(r"\{\s*" + ph.strip("{}") + r"\s*\}", ph, translated)
                if ph not in translated:
                    translated += f" {ph}"
    return translated

def read_pot_file(path):
    """
    Read and return the lines of a .pot file.

    Args:
        path (Path): Path to the .pot file.

    Returns:
        list: Lines of the .pot file.
    """
    return path.read_text(encoding="utf-8").splitlines()

def init_translators(langs):
    """
    Initialize translators for the specified languages.

    Args:
        langs (list): List of language codes.

    Returns:
        dict: Dictionary of language code to translator instances.
    """
    return {lang: GoogleTranslator(source='en', target=lang) for lang in langs}

def add_po_header(lines, lang):
    """
    Add header information to the .po translation file.

    Args:
        lines (list): Translated lines.
        lang (str): Language code.

    Returns:
        list: Lines with header prepended.
    """
    header = [
        'msgid ""',
        'msgstr ""',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        f'"Language: {lang}\\n"',
        ""
    ]
    return header + lines

def translate_lines(lines, translators):
    """
    Translate lines from a .pot file using provided translators.

    Args:
        lines (list): Lines from .pot file.
        translators (dict): Dictionary of translators keyed by language code.

    Returns:
        dict: Translated lines for each language.
    """
    msgid = None
    translated_content = {lang: [] for lang in translators}

    for line in lines:
        if 'fuzzy' in line:
            continue
        if line.startswith('msgid '):
            msgid = line[6:].strip().strip('"')
            for lang in translators:
                translated_content[lang].append(line)
        elif line.strip() == 'msgstr ""' and msgid:
            for lang, translator in translators.items():
                try:
                    translated = translator.translate(msgid)
                    if not translated.strip():
                        print(f"Warning [{lang}] Empty translation for: {msgid}")
                    translated = fix_placeholders(msgid, translated)
                    translated_content[lang].append(f'msgstr "{translated}"')
                    print(f"Translated [{lang}] {msgid} → {translated}")
                except Exception as e:
                    translated_content[lang].append('msgstr ""')
                    print(f"Error [{lang}] translating '{msgid}': {e}")
            msgid = None
        else:
            for lang in translators:
                translated_content[lang].append(line)
    return translated_content

def save_translations(translated_content, base_output_dir):
    """
    Save translated content to .po files.

    Args:
        translated_content (dict): Translations keyed by language.
        base_output_dir (str): Base directory to save translations.
    """
    for lang, lines in translated_content.items():
        lines = add_po_header(lines, lang)
        path = Path(base_output_dir) / lang / "LC_MESSAGES" / "messages.po"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Saved [{lang}] to {path}")

def generate_pot_file():
    """
    Generate .pot file from source files.
    """
    print("Extracting phrases to .pot file ...")
    subprocess.run(["pybabel", "extract", "-F", BABEL_CFG, "-o", POT_FILE, "."], check=True)

def init_po_files(languages):
    """
    Initialize .po translation files for given languages.

    Args:
        languages (list): List of language codes.
    """
    for lang in languages:
        po_path = Path(OUTPUT_DIR) / lang / "LC_MESSAGES" / "messages.po"
        if not po_path.exists():
            print(f"Initializing file for [{lang}] ...")
            subprocess.run(["pybabel", "init", "-i", POT_FILE, "-d", OUTPUT_DIR, "-l", lang], check=True)
        else:
            print(f"Translation file already exists for [{lang}]")

def compile_translations():
    """
    Compile .po files to .mo files.
    """
    try:
        subprocess.run(["pybabel", "compile", "-d", OUTPUT_DIR], check=True)
        print("Compiled translations to .mo files successfully.")
    except subprocess.CalledProcessError as e:
        print("Error compiling .mo files:", e)

def main():
    """
    Main execution function for translation processing.
    """
    if not Path(BABEL_CFG).exists():
        print(f"Missing {BABEL_CFG} file.")
        return

    generate_pot_file()
    init_po_files(LANGUAGES)

    if not Path(POT_FILE).exists():
        print(f"{POT_FILE} not found after extraction.")
        return

    lines = read_pot_file(Path(POT_FILE))
    translators = init_translators(LANGUAGES)
    translated_content = translate_lines(lines, translators)
    save_translations(translated_content, OUTPUT_DIR)
    compile_translations()

    # Remove temporary .pot file
    if Path(POT_FILE).exists():
        Path(POT_FILE).unlink()
        print("Temporary messages.pot file deleted.")

if __name__ == "__main__":
    main()
