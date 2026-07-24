import os

print("Attempting to rename 'classification prediction' to 'classification_prediction'")

for item in os.listdir('.'):
    if 'classification' in item.lower():
        print(f"Found: '{item}'")
        new_name = item.replace(' ', '_')
        try:
            os.rename(item, new_name)
            print(f"✅ Successfully renamed to: '{new_name}'")
        except OSError as e:
            print(f"❌ Error renaming: {e}")
            print(f"Error code: {e.errno}")
