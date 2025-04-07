
import os
import re

def process_file():
    """Process the layout.html file to fix the message display"""
    file_path = "templates/layout.html"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return
    
    # Read the current content
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Define the regex pattern for the messages section to replace
    pattern = r"""    <!-- Flash Messages -->
    
        {% if messages %}
            <div class="container mt-4">
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    """
    
    # Define the replacement
    replacement = """    <!-- Flash Messages -->
    {% if messages %}
        <div class="container mt-4">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            {% endfor %}
        </div>
    {% endif %}
    """
    
    # Perform the replacement
    if pattern in content:
        updated_content = content.replace(pattern, replacement)
        
        # Write the updated content back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(updated_content)
        
        print(f"Successfully updated {file_path}")
    else:
        print(f"The pattern was not found in {file_path}")

if __name__ == "__main__":
    process_file()

