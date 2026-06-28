import os

base_dir = r"courses/global-quality-maternal-and-newborn-care/module-3/01_source_cards"
output_file = os.path.join(base_dir, "combined_source_cards.md")

print("\n--- Automated Source-Card Combiner ---")

if not os.path.exists(base_dir):
    print(f"Error: Target directory does not exist: {base_dir}")
    exit()

# Filter and sort the completed source cards numerically
card_files = sorted([
    f for f in os.listdir(base_dir)
    if f.startswith("source_card_") and f.endswith(".md") and "combined" not in f
])

if not card_files:
    print(f"Error: No completed source cards found in {base_dir}")
    exit()

total_files = len(card_files)
print(f"Found {total_files} source cards. Compiling master file...")

try:
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("# Combined Source Cards Master - Module 3\n\n")
        outfile.write(f"Total Compiled Documents: {total_files}\n\n---\n\n")
        
        for idx, card in enumerate(card_files, start=1):
            card_path = os.path.join(base_dir, card)
            print(f"[{idx}/{total_files}] Merging {card}...")
            
            with open(card_path, 'r', encoding='utf-8') as infile:
                card_content = infile.read()
                
            # Append content with defensive structural spacing
            outfile.write(card_content.strip())
            outfile.write("\n\n\n\n---\n\n\n\n")
            
    print(f"\nSuccess! All cards assembled seamlessly into:")
    print(f"-> {output_file}")

except Exception as e:
    print(f"\nError during compilation: {e}")
