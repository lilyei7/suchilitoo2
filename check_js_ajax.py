import os
import django
import sys
import glob
import re
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sushi_core.settings')
django.setup()

def check_js_ajax_handling():
    """Check all JS files for proper AJAX error handling"""
    print("=== CHECKING JAVASCRIPT AJAX HANDLING ===")
    
    js_files = glob.glob('dashboard/static/dashboard/js/*.js')
    js_files += glob.glob('dashboard/templates/dashboard/*.html')
    
    fetch_pattern = re.compile(r'fetch\s*\(.*?\)\s*\.then\s*\(\s*response\s*=>\s*response\.json\(\)\s*\)', re.DOTALL)
    safe_fetch_pattern = re.compile(r'fetch\s*\(.*?\)\s*\.then\s*\(\s*response\s*=>\s*response\.text\(\)\s*\)', re.DOTALL)
    
    issues_found = 0
    
    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Look for risky patterns
                matches = fetch_pattern.findall(content)
                
                if matches:
                    print(f"\n📄 {js_file}: Found {len(matches)} potentially unsafe AJAX patterns")
                    issues_found += len(matches)
                    
                    for i, match in enumerate(matches[:3]):  # Show first 3 matches only
                        print(f"  🔍 Match {i+1}: {match[:100]}...")
                    
                    # Look for context
                    for match in matches:
                        context_start = content.find(match) - 100
                        context_end = content.find(match) + len(match) + 100
                        context = content[max(0, context_start):min(len(content), context_end)]
                        
                        # Look for error handling
                        if ".catch" in context:
                            print("    ✅ Has error handling with .catch()")
                        else:
                            print("    ❌ No error handling with .catch() found")
                            
                # Look for safer patterns
                safe_matches = safe_fetch_pattern.findall(content)
                if safe_matches:
                    print(f"  ✅ Found {len(safe_matches)} safer AJAX patterns using response.text()")
                    
        except Exception as e:
            print(f"Error processing {js_file}: {e}")
    
    print(f"\n🔍 Found {issues_found} potentially unsafe AJAX patterns in total")
    print("Recommendation: Replace direct response.json() calls with response.text() followed by JSON.parse in a try/catch block")

def check_view_json_responses():
    """Check all view files for proper JSON response handling"""
    print("\n=== CHECKING VIEW JSON RESPONSES ===")
    
    view_files = glob.glob('dashboard/views/**/*.py', recursive=True)
    view_files += glob.glob('dashboard/views.py')
    
    json_response_pattern = re.compile(r'return\s+JsonResponse\s*\(')
    error_handling_pattern = re.compile(r'try\s*:.*?except.*?return\s+JsonResponse', re.DOTALL)
    
    issues_found = 0
    
    for view_file in view_files:
        try:
            with open(view_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Count JSON responses
                json_responses = json_response_pattern.findall(content)
                
                if json_responses:
                    print(f"\n📄 {view_file}: Found {len(json_responses)} JsonResponse calls")
                    
                    # Check for error handling around JSON responses
                    error_handling = error_handling_pattern.findall(content)
                    
                    if len(error_handling) < len(json_responses):
                        print(f"  ⚠️ Only {len(error_handling)} of {len(json_responses)} JsonResponse calls are in try-except blocks")
                        issues_found += 1
                    else:
                        print(f"  ✅ All {len(json_responses)} JsonResponse calls have error handling")
                    
                    # Check for print statements in views with JsonResponse
                    if "print(" in content and len(json_responses) > 0:
                        print(f"  ⚠️ Contains print() statements which might interfere with JSON output")
                        issues_found += 1
                
        except Exception as e:
            print(f"Error processing {view_file}: {e}")
    
    print(f"\n🔍 Found {issues_found} potential issues in view files")
    print("Recommendation: Ensure all JsonResponse calls are in try-except blocks and remove print statements")

if __name__ == "__main__":
    check_js_ajax_handling()
    check_view_json_responses()
