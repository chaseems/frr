import os

# 定义要扫描的目录和输出文件
project_dir = "D:\\Workspace\\Java\\swing_0302\\"  # ./当前目录
output_file = "java_project_context.md"

# 排除不需要的文件夹
exclude_dirs = {'.git', '.idea', 'target', 'build', '.gradle'}
# 仅读取的关键文件后缀
include_extensions = {'.java', '.xml', '.yml', '.properties', '.gradle'}

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write("# Java Project Source Code Context\n\n")
    
    # 1. 简易生成目录树结构
    outfile.write("## 1. Project Structure\n```text\n")
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in include_extensions):
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                outfile.write(f"{rel_path}\n")
    outfile.write("```\n\n## 2. Source Code Files\n\n")
    
    # 2. 遍历并合并代码内容
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in include_extensions):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_dir)
                
                # 写入文件分割标识，方便 AI 识别
                outfile.write(f"### File: {rel_path}\n")
                outfile.write(f"```{file.split('.')[-1]}\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"// Error reading file: {str(e)}")
                outfile.write("\n```\n\n")

print(f"合并完成！生成文件：{output_file}")
