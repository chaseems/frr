import os

# Configuration
project_dir = "./"  # Root directory of the target Java project
output_file = "java_project_llm_context.md"

# 1. Strictly exclude IT/IDE-generated cache and build directories to prevent excessive file size
exclude_dirs = {
    '.git', '.idea', 'target', 'build', '.gradle', 
    '.metadata', '.settings', 'bin', 'out'
}

# 2. Key configuration files and source code extensions that must be included
include_extensions = {
    '.java',          # Java Source Code
    '.xml',           # pom.xml, MyBatis Mappers, etc.
    '.properties',    # application.properties
    '.yml', '.yaml',  # application.yml
    '.gradle'         # Gradle Configurations
}

# 3. Specific filenames allowed regardless of their extension
exact_files_to_include = {'pom.xml', 'build.gradle', 'README.md'}

print("Scanning and purifying Java project...")

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write("# Java Project Comprehensive Context\n\n")
    
    # === Part 1: Generate a Clean Project Directory Tree ===
    outfile.write("## 1. Project Directory Tree\n```text\n")
    for root, dirs, files in os.walk(project_dir):
        # Dynamically filter out excluded directories and hidden folders
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            ext = os.path.splitext(file).lower()
            if ext in include_extensions or file in exact_files_to_include:
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                outfile.write(f"{rel_path}\n")
    outfile.write("```\n\n## 2. Configuration & Source Code\n\n")
    
    # === Part 2: Merge Code and Configuration Files ===
    file_count = 0
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            ext = os.path.splitext(file).lower()
            if ext in include_extensions or file in exact_files_to_include:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_dir)
                
                # Write file anchor for easy recognition by MS Teams Copilot
                outfile.write(f"### FILE_PATH: {rel_path}\n")
                
                # Provide standard Markdown syntax highlighting based on extension
                lang = ext.replace('.', '') if ext else 'text'
                if file == 'pom.xml': 
                    lang = 'xml'
                outfile.write(f"```{lang}\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"// Error reading file content: {str(e)}")
                
                outfile.write("\n```\n\n")
                file_count += 1

print(f"Extraction successful! Packed {file_count} core files.")
print(f"Output saved to: {os.path.abspath(output_file)}")
