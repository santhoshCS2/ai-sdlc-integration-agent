import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MOCK_MODE = os.getenv('MOCK_MODE', 'false').lower() == 'true'
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# API keys configured via environment variables

# Configure Gemini
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("Gemini model initialized successfully")
    except Exception as e:
        print(f"Gemini init error: {e}")
        model = None
else:
    model = None
    print("WARNING: No Gemini API key found")

def fix_code_with_llm(code: str, issues: str, file_path: str) -> str:
    print(f"\n=== Fixing {file_path} ===")
    print(f"MOCK_MODE: {MOCK_MODE}")
    print(f"Issues: {issues}")
    print(f"Original code length: {len(code)}")
    
    if MOCK_MODE:
        print("Using MOCK mode")
        fixed_code = code
        
        # Apply mock fixes based on file type
        if file_path.endswith('.py'):
            # Python fixes
            fixed_code = fixed_code.replace('print "', 'print("')
            fixed_code = fixed_code.replace('"\n', '")\n')
            if 'def calculate' in fixed_code:
                fixed_code = fixed_code.replace('return a / b', 'return a / b if b != 0 else 0  # Fixed division by zero')
            fixed_code += '\n# MOCK: Added error handling and Python 3 compatibility'
            
        elif file_path.endswith('.js'):
            # JavaScript fixes
            if not fixed_code.strip().endswith(';'):
                fixed_code = fixed_code.rstrip() + ';\n'
            fixed_code += '\n// MOCK: Added missing semicolons and formatting'
            
        elif file_path.endswith('.html'):
            # HTML fixes - apply multiple realistic improvements
            # Fix image alt attributes
            fixed_code = re.sub(r'<img([^>]*) alt=""([^>]*)>', r'<img\1 alt="Profile photo"\2>', fixed_code)
            
            # Fix logo path
            fixed_code = fixed_code.replace('logo.png.png', 'logo.png')
            
            # Add form validation
            fixed_code = fixed_code.replace('placeholder="Enter Name">', 'placeholder="Enter Name" required minlength="2">')
            fixed_code = fixed_code.replace('placeholder="Enter Number">', 'placeholder="Enter Number" pattern="[0-9]{10}" required>')
            
            # Add SEO meta tags
            if '<meta name="viewport"' in fixed_code and '<meta name="description"' not in fixed_code:
                fixed_code = fixed_code.replace(
                    '<meta name="viewport" content="width=device-width, initial-scale=1">',
                    '<meta name="viewport" content="width=device-width, initial-scale=1">\n  <meta name="description" content="Find your perfect Telugu matrimony match. Trusted matrimony service with verified profiles.">\n  <meta name="keywords" content="Telugu matrimony, marriage, wedding, bride, groom">'
                )
            
            # Always add mock comment to ensure changes
            fixed_code += '\n<!-- MOCK: Applied accessibility, SEO, and validation improvements -->'
            
            # Fix image alt attributes
            if 'alt=""' in fixed_code:
                fixed_code = fixed_code.replace('alt=""', 'alt="Profile photo"')
            
            # Fix logo path
            if 'logo.png.png' in fixed_code:
                fixed_code = fixed_code.replace('logo.png.png', 'logo.png')
            
            # Add form validation
            if 'placeholder="Enter Name">' in fixed_code:
                fixed_code = fixed_code.replace('placeholder="Enter Name">', 'placeholder="Enter Name" required minlength="2">')
            
            if 'placeholder="Enter Number">' in fixed_code:
                fixed_code = fixed_code.replace('placeholder="Enter Number">', 'placeholder="Enter Number" pattern="[0-9]{10}" required>')
        
        else:
            # Generic fixes
            fixed_code += '\n# MOCK: Applied generic code improvements'
        
        print(f"MOCK: Applied fixes to {file_path}")
        return fixed_code
    
    # Try Groq first (fastest and free)
    if GROQ_API_KEY:
        print("Using Groq API")
        try:
            import requests
            
            prompt = f"""Fix this code issue:

ISSUE: {issues}

CODE:
{code}

Return ONLY the complete fixed code with the issue resolved. Do not include explanations or markdown."""

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}'
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            
            response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=data)
            print(f"Groq API status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                fixed_code = result['choices'][0]['message']['content'].strip()
                
                print(f"Groq response length: {len(fixed_code)}")
                
                # Remove markdown code blocks if present
                if '```' in fixed_code:
                    code_match = re.search(r'```(?:\w+)?\n(.+?)```', fixed_code, re.DOTALL)
                    if code_match:
                        fixed_code = code_match.group(1).strip()
                
                if fixed_code and len(fixed_code) > 10:
                    return fixed_code
            else:
                print(f"Groq API error: {response.text}")
        except Exception:
            pass
    
    # Try OpenAI as fallback
    if OPENAI_API_KEY:
        print("Using OpenAI API")
        try:
            import requests
            
            prompt = f"""Fix this code issue:

ISSUE: {issues}

CODE:
{code}

Return ONLY the complete fixed code with the issue resolved. Do not include explanations or markdown."""

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {OPENAI_API_KEY}'
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            print(f"OpenAI API status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                fixed_code = result['choices'][0]['message']['content'].strip()
                
                print(f"OpenAI response length: {len(fixed_code)}")
                
                # Remove markdown code blocks if present
                if '```' in fixed_code:
                    code_match = re.search(r'```(?:\w+)?\n(.+?)```', fixed_code, re.DOTALL)
                    if code_match:
                        fixed_code = code_match.group(1).strip()
                
                if fixed_code and len(fixed_code) > 10:
                    return fixed_code
            else:
                print(f"OpenAI API error: {response.text}")
        except Exception:
            pass
    
    # Try Gemini if OpenAI fails
    if model and GOOGLE_API_KEY:
        print("Using Gemini API")
        try:
            prompt = f"""Fix this code issue:

ISSUE: {issues}

CODE:
{code}

Return ONLY the complete fixed code with the issue resolved. Do not include explanations or markdown."""
            
            response = model.generate_content(prompt)
            print(f"Gemini API response received")
            
            if response.text:
                fixed_code = response.text.strip()
                print(f"Gemini response length: {len(fixed_code)}")
                
                # Remove markdown code blocks if present
                if '```' in fixed_code:
                    code_match = re.search(r'```(?:\w+)?\n(.+?)```', fixed_code, re.DOTALL)
                    if code_match:
                        fixed_code = code_match.group(1).strip()
                
                if fixed_code and len(fixed_code) > 10:
                    return fixed_code
        except Exception:
            pass
    
    return code
