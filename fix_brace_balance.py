#!/usr/bin/env python3
"""
Fix brace balance by removing extra closing braces
"""

import re

def fix_brace_balance():
    """Fix brace balance"""
    
    html_file = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\recetas.html'
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract JavaScript content
        script_start = content.find('<script>')
        script_end = content.find('</script>') + len('</script>')
        
        if script_start == -1 or script_end == -1:
            print("No JavaScript block found")
            return
        
        before_js = content[:script_start]
        js_with_tags = content[script_start:script_end]
        after_js = content[script_end:]
        
        # Extract just the JS content
        js_match = re.search(r'<script>(.*?)</script>', js_with_tags, re.DOTALL)
        if not js_match:
            print("Could not extract JS content")
            return
            
        js_code = js_match.group(1)
        lines = js_code.split('\n')
        
        # Track brace balance and identify lines with negative balance
        brace_count = 0
        fixed_lines = []
        fixes_made = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            original_line = line
            
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Check if this line would make the balance negative
            new_balance = brace_count + open_braces - close_braces
            
            if new_balance < 0:
                # We need to remove some closing braces
                braces_to_remove = abs(new_balance)
                
                # Remove closing braces from the end of the line first
                modified_line = line
                for _ in range(braces_to_remove):
                    # Find the last closing brace and remove it
                    last_brace_pos = modified_line.rfind('}')
                    if last_brace_pos != -1:
                        modified_line = modified_line[:last_brace_pos] + modified_line[last_brace_pos+1:]
                        fixes_made.append(f"Line {line_num}: Removed closing brace")
                
                fixed_lines.append(modified_line)
                
                # Recalculate balance with fixed line
                new_open = modified_line.count('{')
                new_close = modified_line.count('}')
                brace_count += new_open - new_close
                
            else:
                fixed_lines.append(line)
                brace_count += open_braces - close_braces
        
        if fixes_made:
            # Reconstruct the file
            new_js_code = '\n'.join(fixed_lines)
            new_js_with_tags = f'<script>{new_js_code}</script>'
            new_content = before_js + new_js_with_tags + after_js
            
            # Write back to file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Fixed {len(fixes_made)} brace issues:")
            for fix in fixes_made:
                print(f"  {fix}")
                
            print(f"Final brace balance: {brace_count}")
        else:
            print("No fixes needed")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_brace_balance()
