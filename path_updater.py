import os

def fix_paths(file_path, base_dir):
    with open(file_path, 'r') as f:
        content = f.read()

    # Update hardcoded paths
    updated_content = content.replace(
        '/Users/mspags/',  # Your actual hardcoded path
        f'{base_dir}/'     # Replacing it with the dynamic path
    )

    with open(file_path, 'w') as f:
        f.write(updated_content)

# Define the base directory dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Corrected list of files to update
files_to_update = [
    'dashboard11.py',
    'quote_dashboard.py',
    'followup_tracker.py',
    'referral_tracker.py',
    'achievements1.py',
    'goals1.py',
    'callchallenges.py',
    'completed_challenges.py',
    'lead_metrics.py',
    'metrics_overview.py',
    'visualization.py',
    'conversation_challenges.py'
]

# Update each file
for file in files_to_update:
    file_path = os.path.join(BASE_DIR, file)
    if os.path.exists(file_path):
        print(f"Updating paths in {file_path}")
        fix_paths(file_path, BASE_DIR)
    else:
        print(f"File not found: {file_path}")
