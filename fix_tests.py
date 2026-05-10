import os
import glob
import re

files = glob.glob('tests/test_*.py')

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # Skip if not using AUTH_HEADER
    if 'AUTH_HEADER' not in content and 'dev-token' not in content:
        continue

    # Remove the global AUTH_HEADER assignment
    content = re.sub(r'AUTH_HEADER\s*=\s*\{.*?\n', '', content)
    
    # Replace headers=AUTH_HEADER with headers=admin_token
    content = content.replace('headers=AUTH_HEADER', 'headers=admin_token')
    
    # In test_tags.py, it uses hardcoded headers
    content = content.replace('headers={"Authorization": "Bearer dev-token-change-in-production"}', 'headers=admin_token')
    
    # Add admin_token to test signatures
    # Look for def test_...(...):
    def replacer(match):
        sig = match.group(1)
        if 'admin_token' not in sig:
            if sig.strip():
                new_sig = sig + ', admin_token'
            else:
                new_sig = 'admin_token'
            return f"def {match.group(0)[4:match.group(0).find('(')]}({new_sig}):"
        return match.group(0)

    # For functions
    content = re.sub(r'def test_[^\(]+\((.*?)\):', replacer, content)
    
    with open(f, 'w') as file:
        file.write(content)

print("Test files updated.")
