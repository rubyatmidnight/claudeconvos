import os
import sys
import json
import re

def sanitize_filename(name):
    name = name.replace(' ', '_')
    name = re.sub(r'[^A-Za-z0-9_\-]', '', name)
    return name

def split_conversations(output_dir):
    input_file = "source/conversations.json"
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
    except Exception as e:
        print(f'Failed to parse JSON: {e}', file=sys.stderr)
        sys.exit(1)

    if not isinstance(conversations, list):
        print('Input JSON must be an array of conversation objects.', file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    index_entries = []

    for idx, conv in enumerate(conversations, start=1):
        raw_name = conv.get('name', f'conversation_{idx}')
        # If the name is blank (empty string or only whitespace), rename it Untitled
        if not str(raw_name).strip():
            raw_name = "Untitled"
        safe_name = sanitize_filename(str(raw_name))
        fname = f"{idx:03d}_{safe_name}.json"
        out_path = os.path.join(output_dir, fname.strip())
        with open(out_path, 'w', encoding='utf-8') as out_f:
            json.dump(conv, out_f, indent=2, ensure_ascii=True)
        print(f"Wrote: {out_path}")

        entry = {
            "index": idx,
            "name": raw_name,
            "filename": fname,
            "uuid": conv.get("uuid", None)
        }
        index_entries.append(entry)

    index_path = os.path.join(output_dir, "index.json")
    with open(index_path, 'w', encoding='utf-8') as idx_f:
        json.dump(index_entries, idx_f, indent=2, ensure_ascii=True)
    print(f"Wrote index: {index_path}")

if __name__ == '__main__':
    output_dir = "convos/"
    split_conversations(output_dir)
