import os
import time

try:
    import google.generativeai as genai
except ImportError:
    print("Error: The google-generativeai library is not installed. Please run 'pip install google-generativeai' in PowerShell.")
    exit()

# Configuration and API Key placement
import os

# Securely fetch the API key from the system environment
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable is missing.")
    return
genai.configure(api_key=API_KEY)

# Directory configurations
base_dir = r"courses/global-quality-maternal-and-newborn-care/module-3/01_source_cards"
prompt_package_dir = os.path.join(base_dir, "source_card_prompt_package_20260628113233")

print("\n--- Fully Automated Gemini API Source-Card Generator ---")

if not os.path.exists(prompt_package_dir):
    print(f"Error: Prompt package directory not found at: {prompt_package_dir}")
    exit()

# Safety and extraction rules applied directly to the model
system_rules = (
    "You are a highly precise data extraction engine. Output strictly in Markdown format. "
    "Restrict extraction to operational healthcare tools, procedures, and clinical workflows. "
    "Do not include generic wellness or beauty products. "
    "Never generate fictional diagnostic metrics or precision percentages; only use externally measured data. "
    "Treat every URL context as an isolated ingestion event to prevent continuity errors."
)

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_rules
)

# Read and sort prompt files matching the structure from Stage 1
prompt_files = sorted([
    f for f in os.listdir(prompt_package_dir) 
    if f.startswith('source_card_prompt_') and f.endswith('.md')
])
total_cards = len(prompt_files)

for idx, prompt_file in enumerate(prompt_files, start=1):
    filename = f"source_card_{idx:02d}.md"
    filepath = os.path.join(base_dir, filename)
    prompt_filepath = os.path.join(prompt_package_dir, prompt_file)
    
    # Skip processing if the source card file already has data written to it
    if os.path.exists(filepath) and os.path.getsize(filepath) > 200:
        print(f"[{idx}/{total_cards}] {filename} already contains data. Skipping.")
        continue
        
    print(f"[{idx}/{total_cards}] Sending {prompt_file} to Gemini API...")
    
    with open(prompt_filepath, 'r', encoding='utf-8') as pf:
        prompt_content = pf.read()
        
    try:
        # Request content from Google AI Studio servers
        response = model.generate_content(prompt_content)
        
        # Save response string into a clean Markdown file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Source Card {idx:02d}\n\n")
            f.write(response.text)
            
        print(f"    -> Success! Saved text data seamlessly to {filename}")
        
        # Free tier rate limit mitigation delay
        time.sleep(3) 
        
    except Exception as e:
        print(f"    -> Error processing {filename}: {e}")

print("\nAll automated source cards are complete. You can now close this script and run Option 4 in your main manager.")