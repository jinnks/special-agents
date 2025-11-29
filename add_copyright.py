#!/usr/bin/env python3
"""
Script to add copyright headers to all Python files in the project

Copyright (c) 2025 Special Agents
Licensed under MIT License - See LICENSE file for details
"""

import os
import glob

COPYRIGHT_HEADER = '''# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

'''

def add_copyright_to_file(filepath):
    """Add copyright header to a Python file if not already present"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Skip if copyright already exists
    if 'Copyright (c) 2025 Special Agents' in content:
        print(f"✓ Already has copyright: {filepath}")
        return False

    # Skip empty files
    if not content.strip():
        print(f"⊘ Empty file, skipping: {filepath}")
        return False

    # Add copyright at the top
    new_content = COPYRIGHT_HEADER + content

    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"✓ Added copyright to: {filepath}")
    return True

def main():
    # Find all Python files in backend/app
    app_dir = '/home/fsiddiqui/special-agents/backend/app'
    python_files = []

    for root, dirs, files in os.walk(app_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    # Also add to run.py
    python_files.append('/home/fsiddiqui/special-agents/backend/run.py')

    print(f"Found {len(python_files)} Python files")
    print("-" * 50)

    updated = 0
    for filepath in python_files:
        if add_copyright_to_file(filepath):
            updated += 1

    print("-" * 50)
    print(f"Updated {updated} files")

if __name__ == '__main__':
    main()
