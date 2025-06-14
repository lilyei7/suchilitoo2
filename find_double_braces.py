#!/usr/bin/env python3
"""
Find double closing braces in JavaScript only
"""

import re

def find_double_braces():
    """Find double closing braces in JS"""
    
    html_file = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\recetas.html'
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract JavaScript content
        script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
        
        if not script_match:
            print("No JavaScript block found")
            return
        
        js_code = script_match.group(1)
        lines = js_code.split('\n')
        
        # Look for patterns that suggest extra braces
        problem_patterns = [
            r'}\s*}',  # Two closing braces
            r'}\s*}\s*catch',  # Brace before catch
            r'}\s*}\s*finally',  # Brace before finally
            r'}\s*}\s*else',  # Brace before else
        ]
        
        problems_found = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            for pattern in problem_patterns:
                if re.search(pattern, line):
                    problems_found.append((line_num, line.strip(), pattern))
        
        if problems_found:
            print("Potential problems found:")
            for line_num, line_content, pattern in problems_found:
                print(f"Line {line_num}: {line_content}")
                print(f"  Pattern: {pattern}")
                print()
        else:
            print("No obvious double brace patterns found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_double_braces()
