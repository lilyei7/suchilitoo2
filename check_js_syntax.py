import re
import sys

def check_javascript_syntax(filepath):
    """
    Check for common JavaScript syntax issues in a file
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
        errors = []
        
        # Check for unclosed template literals
        template_literals = re.findall(r'`[^`]*$', content)
        if template_literals:
            errors.append(f"Found {len(template_literals)} unclosed template literals (backticks)")
        
        # Check for extra parentheses
        extra_parens = re.findall(r'\)\s*\}([^)]|$)', content)
        if extra_parens:
            errors.append(f"Found {len(extra_parens)} occurrences of '}}), possible syntax error")
        
        # Check for properly formatted .then() chains
        if '.then(' in content:
            then_count = content.count('.then(')
            catch_count = content.count('.catch(')
            if then_count > 0 and catch_count == 0:
                errors.append(f"Found {then_count} .then() calls but no .catch() calls")
            
        # Check for mismatched function parentheses in arrow functions
        arrow_funcs = re.findall(r'=>\s*{[^}]*$', content)
        if arrow_funcs:
            errors.append(f"Found {len(arrow_funcs)} potentially unclosed arrow functions")
        
        # Check for indentation issues after fetch
        fetch_indentation = re.findall(r'fetch\(\s*[^)]*\)\s*\{', content)
        if fetch_indentation:
            errors.append(f"Found {len(fetch_indentation)} fetch calls with incorrect indentation")
        
        # Check for missing semicolons at statement endings
        # This is a basic check and might have false positives
        missing_semicolons = re.findall(r'(const|let|var)\s+\w+\s*=\s*[^;{]*\n', content)
        if missing_semicolons:
            errors.append(f"Found {len(missing_semicolons)} potential missing semicolons in variable declarations")
        
        return errors
        
    except Exception as e:
        return [f"Error reading file: {str(e)}"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <filepath>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    errors = check_javascript_syntax(filepath)
    
    if errors:
        print(f"Found {len(errors)} potential syntax issues:")
        for error in errors:
            print(f"- {error}")
    else:
        print("No common syntax issues found.")
