import os
import subprocess

base_dir = r"courses/global-quality-maternal-and-newborn-care/module-3/01_source_cards"
os.makedirs(base_dir, exist_ok=True)

print("\n--- Sequential Notepad Source-Card Editor ---")
print("Instructions: Paste your LLM output into Notepad, press Ctrl+S to save, and close the window. The next card will open automatically.\n")

for i in range(1, 13):
    filename = f"source_card_{i:02d}.md"
    filepath = os.path.join(base_dir, filename)
    
    # Initialize the file with a header if it does not exist
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Source Card {i:02d}\n\n")
            
    print(f"[{i}/12] Opening {filename}...")
    subprocess.run(["notepad.exe", filepath])

print("\nAll 12 source cards have been processed and saved successfully.")
