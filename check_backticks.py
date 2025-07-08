import sys

def check_backticks(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    open_backticks = 0
    line_num = 1
    unclosed_positions = []
    
    for i, char in enumerate(content):
        if char == '\n':
            line_num += 1
            
        if char == '`':
            if open_backticks % 2 == 0:  # Opening backtick
                open_backticks += 1
                unclosed_positions.append((i, line_num))
            else:  # Closing backtick
                open_backticks -= 1
                unclosed_positions.pop()
    
    if open_backticks > 0:
        print(f"Found {open_backticks} unclosed backticks at positions:")
        for pos, line in unclosed_positions:
            context_start = max(0, pos - 20)
            context_end = min(len(content), pos + 20)
            context = content[context_start:context_end].replace('\n', '\\n')
            print(f"Line {line}, position {pos}: ...{context}...")
    else:
        print("All backticks are properly closed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_backticks.py <filepath>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    check_backticks(filepath)
