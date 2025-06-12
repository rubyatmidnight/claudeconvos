import sys
import json
import os
import difflib


# version: 1.0

LAVENDER = "\033[38;2;181;126;220m"
SKY_BLUE = "\033[38;2;135;206;235m"
PALE_GREEN = "\033[38;2;152;251;152m"
RESET = "\033[0m"

def supports_color():
    if sys.platform == "win32":
        return os.getenv("ANSICON") is not None or \
               os.getenv("WT_SESSION") is not None or \
               'TERM' in os.environ and os.environ['TERM'] == 'xterm'
    if not hasattr(sys.stdout, "isatty"):
        return False
    return sys.stdout.isatty()

COLOR_ENABLED = supports_color()

def color_sky_blue(text):
    if COLOR_ENABLED:
        return f"{SKY_BLUE}{text}{RESET}"
    return text

def color_pale_green(text):
    if COLOR_ENABLED:
        return f"{PALE_GREEN}{text}{RESET}"
    return text

def color_lavender(text):
    if COLOR_ENABLED:
        return f"{LAVENDER}{text}{RESET}"
    return text

def short_text(text, max_lines=15):
    lines = text.strip().splitlines()
    if len(lines) > max_lines:
        return "\n".join(lines[:max_lines]) + "\n... (truncated)"
    return text.strip()

def is_truncated(text, max_lines=15):
    lines = text.strip().splitlines()
    return len(lines) > max_lines

SETTINGS = {
    "assistant_display": "Assistant",
    "human_display": "User"
}

def settings_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(color_sky_blue("=== Settings Menu ==="))
        print(f"1. Assistant display name: {color_lavender(SETTINGS['assistant_display'])}")
        print(f"2. User display name:      {color_lavender(SETTINGS['human_display'])}")
        print("3. Reset to defaults")
        print("4. Return to previous menu")
        print("\nEnter the number to change, or [4] to return: ", end="", flush=True)
        choice = input().strip()
        if choice == "1":
            print("Enter new Assistant display name: ", end="", flush=True)
            new_name = input().strip()
            if new_name:
                SETTINGS["assistant_display"] = new_name
        elif choice == "2":
            print("Enter new User display name: ", end="", flush=True)
            new_name = input().strip()
            if new_name:
                SETTINGS["human_display"] = new_name
        elif choice == "3":
            SETTINGS["assistant_display"] = "Assistant"
            SETTINGS["human_display"] = "User"
            print("Settings reset to defaults. Press Enter to continue.")
            input()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Press Enter to continue.")
            input()

def get_display_sender(sender):
    if sender.lower() == "assistant":
        return SETTINGS["assistant_display"]
    elif sender.lower() == "human":
        return SETTINGS["human_display"]
    else:
        return sender

def display_message(msg, idx, total, focused=False, unfurled=False):
    sender = msg.get("sender", "")
    text = msg.get("text", "")
    display_sender = get_display_sender(sender)
    is_assistant = sender.lower() == "assistant"
    is_human = sender.lower() == "human"
    header = f"\n[{idx+1}/{total}] {display_sender}:"
    truncated = is_truncated(text)
    if is_assistant:
        print(color_sky_blue(header))
        if focused and truncated and not unfurled:
            print(color_lavender(short_text(text)))
            print(color_pale_green("[Press 'u' to unfurl full message]"))
        elif focused and truncated and unfurled:
            print(color_lavender(text.strip()))
        else:
            print(color_lavender(short_text(text)))
    elif is_human:
        print(header)
        if focused and truncated and not unfurled:
            print(short_text(text))
            print("[Press 'u' to unfurl full message]")
        elif focused and truncated and unfurled:
            print(text.strip())
        else:
            print(short_text(text))
    else:
        print(header)
        if focused and truncated and not unfurled:
            print(short_text(text))
            print("[Press 'u' to unfurl full message]")
        elif focused and truncated and unfurled:
            print(text.strip())
        else:
            print(short_text(text))
    if msg.get("attachments"):
        att_str = f"  [Attachments: {len(msg['attachments'])}]"
        print(color_lavender(att_str) if is_assistant else att_str)

def display_last_messages(messages, idx, window=4, unfurled=False):
    total = len(messages)
    start = max(0, idx - window + 1)
    for i in range(start, idx + 1):
        focused = (i == idx)
        display_message(messages[i], i, total, focused=focused, unfurled=(unfurled if focused else False))
        print("-" * 30)

def get_single_keypress():
    try:
        import termios
        import tty
        import sys
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except ImportError:
        import msvcrt
        ch = msvcrt.getch()
        if ch in b'\x00\xe0':  # Arrow or function key prefix
            ch = msvcrt.getch()
        try:
            return ch.decode()
        except Exception:
            return ''
    except Exception:
        return input()[0]

def display_conversation(conv):
    print(f"\n=== {conv.get('name', 'Untitled Conversation')} ===")
    print(f"UUID: {conv.get('uuid', '')}")
    print(f"Created: {conv.get('created_at', '')}")
    print(f"Updated: {conv.get('updated_at', '')}")
    messages = conv.get('chat_messages', [])
    print(f"Messages: {len(messages)}")
    print("="*40)
    idx = 0  
    total = len(messages)
    unfurled = False  # Track if the focused message is unfurled
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n=== {conv.get('name', 'Untitled Conversation')} ===")
        display_last_messages(messages, idx, window=4, unfurled=unfurled)
        print("\nnext [r], prev [e], quit [p], [#] jump to message, [u]nfurl, [o]ptions")
        print("...", end="", flush=True)
        cmd = get_single_keypress()
        if cmd == "\r" or cmd == "\n":
            cmd = "r"
        cmd = cmd.strip().lower()
        # Check if focused message is truncated
        focused_msg = messages[idx] if 0 <= idx < total else None
        focused_truncated = False
        if focused_msg:
            focused_truncated = is_truncated(focused_msg.get("text", ""))
        if cmd == "r" or cmd == "":
            if idx < total - 1:
                idx += 1
                unfurled = False
            else:
                print("End of conversation.")
                print("Press any key to exit.")
                get_single_keypress()
                break
        elif cmd == "e":
            if idx > 0:
                idx -= 1
                unfurled = False
        elif cmd == "p":
            break
        elif cmd == "u":
            if focused_truncated:
                unfurled = True
            else:
                # No effect if not truncated
                pass
        elif cmd == "o":
            settings_menu()
        elif cmd.isdigit():
            num_str = cmd
            print(num_str, end="", flush=True)
            while True:
                next_ch = get_single_keypress()
                if next_ch.isdigit():
                    num_str += next_ch
                    print(next_ch, end="", flush=True)
                else:
                    break
            try:
                num = int(num_str)
                if 1 <= num <= total:
                    idx = num - 1
                    unfurled = False
            except Exception:
                pass
        else:
            print("\nUnknown command.")
            print("Press any key to continue.")
            get_single_keypress()

def load_index(index_path="convos/index.json"):
    if not os.path.exists(index_path):
        convos_dir = os.path.dirname(index_path)
        if not os.path.exists(convos_dir) or not any(
            fname.endswith(".json") and fname != "index.json"
            for fname in os.listdir(convos_dir)
        ):
            print("No conversations found in 'convos/'. Opening 'test.json' instead.")
            if not os.path.exists("test.json"):
                print("test.json not found. Exiting.")
                sys.exit(1)
            with open("test.json", "r", encoding="utf-8") as f:
                try:
                    conv = json.load(f)
                except Exception as e:
                    print(f"Failed to parse test.json: {e}")
                    sys.exit(1)
            return [{
                "index": 1,
                "name": conv.get("name", "Test Conversation"),
                "filename": "test.json",
                "uuid": conv.get("uuid", None)
            }]
        else:
            print(f"Index file not found: {index_path}")
            sys.exit(1)
    with open(index_path, "r", encoding="utf-8") as f:
        try:
            index = json.load(f)
        except Exception as e:
            print(f"Failed to parse index: {e}")
            sys.exit(1)
    return index

def fuzzy_search_index(index, query, max_results=15):
    # Search by name, filename, uuid (case-insensitive, partial, fuzzy)
    query = query.lower()
    scored = []
    for entry in index:
        name = str(entry.get("name", "")).lower()
        fname = str(entry.get("filename", "")).lower()
        score = 0
        if query in name or query in fname:
            score = 100
        else:
            # Fuzzy match on name and filename
            score = max(
                difflib.SequenceMatcher(None, query, name).ratio(),
                difflib.SequenceMatcher(None, query, fname).ratio(),
            ) * 100
        if score > 30:  # Only show reasonably close matches
            scored.append((score, entry))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [e for s, e in scored[:max_results]]

def display_main_menu(index, page=0, page_size=12, search_results=None, search_query=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(color_sky_blue("=== Conversation Explorer ==="))
    if search_results is not None:
        print(color_sky_blue(f"Search results for: '{search_query}'"))
        entries = search_results
        total = len(entries)
        print(f"Found {total} matching conversations.\n")
    else:
        entries = index
        total = len(entries)
        print(f"Found {total} conversations.\n")
    # Pagination
    num_pages = max(1, (total + page_size - 1) // page_size)
    page = max(0, min(page, num_pages - 1))
    start = page * page_size
    end = min(start + page_size, total)
    for i, entry in enumerate(entries[start:end], start=start):
        idx = entry.get("index", "?")
        name = entry.get("name", "Untitled")
        fname = entry.get("filename", "")
        uuid = entry.get("uuid", "")
        print(f"{str(idx).rjust(3)}. {color_lavender(name)}")
        print(f"     {color_pale_green(fname)}")
    print(f"\nPage {page+1}/{num_pages}")
    print("Enter conversation number to open, prev page [e], next page [r], [f]ind, [o]ptions, or 'p' to quit.")

def main_menu_loop(index):
    page = 0
    page_size = 12
    search_results = None
    search_query = None
    while True:
        display_main_menu(index, page=page, page_size=page_size, search_results=search_results, search_query=search_query)
        # Use get_single_keypress for menu navigation and number entry
        choice = get_single_keypress()
        if choice == "\r" or choice == "\n":
            continue
        choice = choice.strip().lower()
        if choice == "p":
            print("Exiting...")
            sys.exit(0)
        elif choice == "e":
            # Previous page, wrap to last page if at first page
            entries = search_results if search_results is not None else index
            total = len(entries)
            num_pages = max(1, (total + page_size - 1) // page_size)
            if page > 0:
                page -= 1
            else:
                page = num_pages - 1
        elif choice == "r":
            # Next page, wrap to first page if at last page
            entries = search_results if search_results is not None else index
            total = len(entries)
            num_pages = max(1, (total + page_size - 1) // page_size)
            if page < num_pages - 1:
                page += 1
            else:
                page = 0
        elif choice == "f":
            # Fuzzy search
            print("Enter search query: ", end="", flush=True)
            # For search query, use input() for full line
            query = input().strip()
            if not query:
                search_results = None
                search_query = None
                page = 0
            else:
                results = fuzzy_search_index(index, query)
                if not results:
                    print("No matches found.")
                    print("Press any key to continue...")
                    get_single_keypress()
                    search_results = None
                    search_query = None
                    page = 0
                else:
                    search_results = results
                    search_query = query
                    page = 0
        elif choice == "o":
            settings_menu()
        elif choice.isdigit():
            # Allow multi-digit entry using get_single_keypress
            num_str = choice
            print(num_str, end="", flush=True)
            while True:
                next_ch = get_single_keypress()
                if next_ch.isdigit():
                    num_str += next_ch
                    print(next_ch, end="", flush=True)
                else:
                    break
            try:
                num = int(num_str)
                entries = search_results if search_results is not None else index
                entry = next((e for e in entries if e.get("index") == num), None)
                if not entry:
                    print(f"\nNo conversation with number {num} on this page.")
                    print("Press any key to continue...")
                    get_single_keypress()
                    continue
                # If the entry is from test.json, open test.json directly
                if entry.get("filename") == "test.json":
                    conv_path = "test.json"
                else:
                    conv_path = os.path.join("convos", entry.get("filename", ""))
                if not os.path.exists(conv_path):
                    print(f"\nConversation file not found: {conv_path}")
                    print("Press any key to continue...")
                    get_single_keypress()
                    continue
                with open(conv_path, "r", encoding="utf-8") as f:
                    try:
                        conv = json.load(f)
                    except Exception as e:
                        print(f"\nFailed to load conversation: {e}")
                        print("Press any key to continue...")
                        get_single_keypress()
                        continue
                display_conversation(conv)
            except Exception:
                print("\nInvalid number.")
                get_single_keypress()
        elif choice == "":
            continue
        else:
            print("\nPlease enter a valid number, [e], [r], [f], [o], or 'p'.")
            get_single_keypress()

def main():
    index = load_index()
    main_menu_loop(index)

if __name__ == "__main__":
    main()
