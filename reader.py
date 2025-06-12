import sys
import json
import os

# ANSI color codes for lavender (foreground)
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

def display_message(msg, idx, total):
    sender = msg.get("sender", "")
    text = msg.get("text", "")
    is_assistant = sender.lower() == "assistant"
    header = f"\n[{idx+1}/{total}] {sender}:"
    if is_assistant:
        print(color_sky_blue(header))
        print(color_lavender(short_text(text)))
    else:
        print(header)
        print(short_text(text))
    if msg.get("attachments"):
        att_str = f"  [Attachments: {len(msg['attachments'])}]"
        print(color_lavender(att_str) if is_assistant else att_str)

def display_last_messages(messages, idx, window=4):
    total = len(messages)
    start = max(0, idx - window + 1)
    for i in range(start, idx + 1):
        display_message(messages[i], i, total)
        print("-" * 30)

def get_single_keypress():
    """
    Wait for a single keypress on the console and return it as a string.
    Works on Windows and Unix.
    """
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
        # Windows
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
    idx = 0  # Start from the beginning of the conversation
    total = len(messages)
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n=== {conv.get('name', 'Untitled Conversation')} ===")
        display_last_messages(messages, idx, window=4)
        print("\n[n]ext, [p]rev, [q]uit, [#]jump to message")
        print("Command: ", end="", flush=True)
        cmd = get_single_keypress()
        if cmd == "\r" or cmd == "\n":
            cmd = "n"
        cmd = cmd.strip().lower()
        if cmd == "n" or cmd == "":
            if idx < total - 1:
                idx += 1
            else:
                print("End of conversation.")
                print("Press any key to exit.")
                get_single_keypress()
                break
        elif cmd == "p":
            if idx > 0:
                idx -= 1
        elif cmd == "q":
            break
        elif cmd.isdigit():
            # Read more digits if available
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
            except Exception:
                pass
        else:
            print("\nUnknown command.")
            print("Press any key to continue.")
            get_single_keypress()

def main():
    if len(sys.argv) < 2:
        print("Usage: python reader.py conversation.json")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        conv = json.load(f)
    display_conversation(conv)

if __name__ == "__main__":
    main()
