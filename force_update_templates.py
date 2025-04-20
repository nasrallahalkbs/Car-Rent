
import os
import time

def force_update_templates():
    '''
    Add timestamp comment to template files to force browser reload
    '''
    templates_dir = 'templates/admin'
    timestamp = int(time.time())
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove previous cache buster comments
                content = content.replace('<!-- CACHE_BUSTER -->', '')
                
                # Add new timestamp comment
                content = f'<!-- CACHE_BUSTER {timestamp} -->' + content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Updated {file_path}")
    
    # Update CSS files too
    css_dir = 'static/css'
    if os.path.exists(css_dir):
        for file in os.listdir(css_dir):
            if file.endswith('.css'):
                file_path = os.path.join(css_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove previous cache buster comments
                content = content.replace('/* CACHE_BUSTER */', '')
                
                # Add new timestamp comment
                content = f'/* CACHE_BUSTER {timestamp} */\n' + content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Updated {file_path}")

if __name__ == "__main__":
    force_update_templates()
    print("All files updated successfully. Please restart the server and reload the page.")
