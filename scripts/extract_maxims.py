"""Extract maxims from AWW.docx into structured JSON."""
import json
import re
import sys
import os
from docx import Document

ROMAN_VALS = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}

def roman_to_int(s):
    s = s.upper()
    total = 0
    for i, c in enumerate(s):
        if c not in ROMAN_VALS:
            return None
        if i + 1 < len(s) and ROMAN_VALS.get(c, 0) < ROMAN_VALS.get(s[i+1], 0):
            total -= ROMAN_VALS[c]
        else:
            total += ROMAN_VALS[c]
    return total

def is_valid_roman(s):
    """Check if string is a valid Roman numeral (not just letters that happen to be roman)."""
    if not re.match(r'^[ivxlcdmIVXLCDM]+$', s):
        return False
    # Reject common English words that look like roman numerals
    reject = {'ill', 'did', 'mid', 'dim', 'mil', 'mix', 'vim', 'civil', 'livid', 'mild', 'vivid'}
    if s.lower() in reject:
        return False
    return True

# Known corrections for OCR/typo errors in the document
CORRECTIONS = {
    # (wrong_numeral, context_hint): correct_id
    # Paragraph with "xxv Think over Things" that should be xxxv
    # Paragraph with "viii Let each keep up his Dignity" that should be ciii
    # Paragraph with "civil Do not make Mistakes" that should be clvii
}

def extract_maxims(docx_path):
    doc = Document(docx_path)
    maxims = []
    current = None
    seen_ids = set()

    for para_idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue

        # Skip page numbers
        if re.match(r'^p\.\s*\d+$', text):
            continue

        # Check for mid-paragraph maxim header (e.g., "...scapegoat. cl Know to get")
        # Handle the cl (150) case embedded in paragraph 458
        mid_match = re.search(r'\.\s+((?:cc?[lxvi]+|[lxvi]+))\s*[\xa0\u00a0]\s*(.+)$', text)

        # Special case: "civil" is a typo for "clvii" (157) in the document
        if text.lower().startswith('civil\xa0') or text.lower().startswith('civil '):
            civil_match = re.match(r'^civil\s*[\xa0\u00a0]\s*(.+)$', text, re.IGNORECASE)
            if civil_match and 157 not in seen_ids:
                if current:
                    maxims.append(current)
                current = {
                    'id': 157,
                    'numeral': 'clvii',
                    'title': civil_match.group(1).strip().rstrip(':;.,'),
                    'body': ''
                }
                seen_ids.add(157)
                continue

        # Check if this is a maxim header: starts with roman numeral + non-breaking space or dash
        match = re.match(r'^([ivxlcdm]+)\s*[\xa0\u00a0—\-–]\s*(.+)$', text, re.IGNORECASE)
        if match and is_valid_roman(match.group(1)):
            numeral_str = match.group(1).lower()
            num = roman_to_int(numeral_str)
            title = match.group(2).strip().rstrip(':;.,')

            if num and 1 <= num <= 300:
                # Handle known duplicate corrections:
                # If we've already seen this ID, it's a document error
                if num in seen_ids:
                    # "xxv" appearing second time should be "xxxv" (35)
                    if num == 25 and 'Think over Things' in title:
                        num = 35
                        numeral_str = 'xxxv'
                    # "viii" appearing second time should be "ciii" (103)
                    elif num == 8 and 'Let each keep up' in title:
                        num = 103
                        numeral_str = 'ciii'
                    # "xcix" appearing second time as "ill" matched wrongly
                    elif num == 99:
                        # This is body text, skip as header
                        if current:
                            if current['body']:
                                current['body'] += ' '
                            current['body'] += text
                        continue
                    # "cliii" appearing second as "civil" -> should be clvii (157)
                    elif num == 153 and 'Mistakes about Character' in title:
                        num = 157
                        numeral_str = 'clvii'

                if current:
                    maxims.append(current)
                current = {
                    'id': num,
                    'numeral': numeral_str,
                    'title': title,
                    'body': ''
                }
                seen_ids.add(num)
                continue

        # Check for mid-paragraph maxim (like cl embedded in text)
        if mid_match and is_valid_roman(mid_match.group(1)):
            numeral_str = mid_match.group(1).lower()
            num = roman_to_int(numeral_str)
            if num and 1 <= num <= 300 and num not in seen_ids:
                # Add the text before the numeral to the current maxim's body
                before_text = text[:mid_match.start(1)].strip().rstrip('.')
                if current and before_text:
                    if current['body']:
                        current['body'] += ' '
                    current['body'] += before_text

                if current:
                    maxims.append(current)
                current = {
                    'id': num,
                    'numeral': numeral_str,
                    'title': mid_match.group(2).strip().rstrip(':;.,'),
                    'body': ''
                }
                seen_ids.add(num)
                continue

        # Otherwise it's body text for the current maxim
        if current:
            if current['body']:
                current['body'] += ' '
            current['body'] += text

    if current:
        maxims.append(current)

    return maxims

def main():
    docx_path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\edcoo\OneDrive\AWW.docx'
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(out_dir, exist_ok=True)

    maxims = extract_maxims(docx_path)
    maxims.sort(key=lambda m: m['id'])

    out_path = os.path.join(out_dir, 'maxims_raw.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(maxims, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(maxims)} maxims to {out_path}")

    # Quick validation
    ids = [m['id'] for m in maxims]
    missing = [i for i in range(1, 301) if i not in ids]
    if missing:
        print(f"WARNING: Missing maxim IDs: {missing}")
    dupes = [i for i in ids if ids.count(i) > 1]
    if dupes:
        print(f"WARNING: Duplicate IDs: {set(dupes)}")

    # Show a few
    for m in maxims[:5]:
        print(f"  {m['id']} ({m['numeral']}): {m['title'][:50]}")

if __name__ == '__main__':
    main()
