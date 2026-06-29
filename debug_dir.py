import os
base_dir = r"courses/global-quality-maternal-and-newborn-care/module-3/01_source_cards"
prompt_package_dir = os.path.join(base_dir, "source_card_prompt_package_20260628113233")

if os.path.exists(prompt_package_dir):
    print(f"Directory found: {prompt_package_dir}")
    files = os.listdir(prompt_package_dir)
    print(f"Files found: {files}")
else:
    print(f"Directory NOT found at: {prompt_package_dir}")