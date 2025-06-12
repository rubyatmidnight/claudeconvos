# Tool to split a JSON file into separate JSON files per conversation

import os
import sys
import json
import re

def sanitize_filename(name):
    # Replace spaces with underscores and remove special characters
    name = name.replace(' ', '_')
    # Remove any character that is not alphanumeric, underscore, or hyphen
    name = re.sub(r'[^A-Za-z0-9_\-]', '', name)
    return name

def split_conversations(input_file, output_dir):
    # Read and parse the input JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
    except Exception as e:
        print(f'Failed to parse JSON: {e}', file=sys.stderr)
        sys.exit(1)

    if not isinstance(conversations, list):
        print('Input JSON must be an array of conversation objects.', file=sys.stderr)
        sys.exit(1)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write each conversation to its own file
    for idx, conv in enumerate(conversations):
        raw_name = conv.get('name', f'conversation_{idx}')
        safe_name = sanitize_filename(str(raw_name))
        fname = f"{safe_name}.json"
        out_path = os.path.join(output_dir, fname.strip())
        with open(out_path, 'w', encoding='utf-8') as out_f:
            json.dump(conv, out_f, indent=2, ensure_ascii=True)
        print(f"Wrote: {out_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python Untitled-2.py input.json output_dir')
        sys.exit(1)
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    split_conversations(input_file, output_dir)
