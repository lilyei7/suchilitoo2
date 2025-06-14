#!/usr/bin/env python3
"""
Find brace imbalance without emojis - write to file
"""

import re

def find_brace_imbalance_simple():
    """Find brace imbalance"""
    
    html_file = r'c:\Users\olcha\Desktop\sushi_restaurant\dashboard\templates\dashboard\recetas.html'
    output_file = r'c:\Users\olcha\Desktop\sushi_restaurant\brace_analysis.txt'
    
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
        
        # Count braces per line
        brace_count = 0
        line_number = 0
        
        output_lines = []
        output_lines.append("Analyzing brace balance line by line:")
        output_lines.append("=" * 60)
        
        problem_lines = []
        
        for i, line in enumerate(lines):
            line_number = i + 1
            open_braces = line.count('{')
            close_braces = line.count('}')
            brace_count += open_braces - close_braces
            
            if open_braces > 0 or close_braces > 0:
                status = "OK" if brace_count >= 0 else "ERROR"
                output_lines.append(f"{status} Line {line_number:4d}: +{open_braces} -{close_braces} = {brace_count:3d} | {line.strip()[:70]}")
                
                if brace_count < 0:
                    problem_lines.append((line_number, line.strip()))
        
        output_lines.append("=" * 60)
        output_lines.append(f"Final balance: {brace_count}")
        
        if brace_count != 0:
            output_lines.append(f"ERROR: Brace balance incorrect ({brace_count})")
            
            # Find lines with extra closing braces
            output_lines.append("\nLines that might have extra closing braces:")
            for line_num, line_content in problem_lines[-10:]:
                output_lines.append(f"Line {line_num:4d}: {line_content}")
                
        else:
            output_lines.append("Brace balance correct")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print(f"Analysis written to {output_file}")
        print(f"Final balance: {brace_count}")
        
        # Just print the problematic lines
        if problem_lines:
            print("Problem lines:")
            for line_num, line_content in problem_lines[-5:]:
                print(f"Line {line_num}: {line_content}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_brace_imbalance_simple()
