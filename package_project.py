import os
import zipfile
from pathlib import Path
import fnmatch

def load_gitignore_patterns(workspace_dir):
    """Loads patterns from .gitignore file if it exists."""
    gitignore_path = Path(workspace_dir) / ".gitignore"
    patterns = []
    if gitignore_path.exists():
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)
    # Always ensure standard hygiene rules are enforced
    if ".env" not in patterns:
        patterns.append(".env")
    if "backend/.env" not in patterns:
        patterns.append("backend/.env")
    return patterns

def should_ignore(path, root_dir, patterns):
    """Checks if a path matches any .gitignore pattern."""
    relative_path = path.relative_to(root_dir).as_posix()
    
    # Check each pattern against relative path or any of its parent segments
    parts = relative_path.split("/")
    for pattern in patterns:
        # Normalize pattern trailing slash
        clean_pattern = pattern.rstrip("/")
        
        # Match complete path or part of path (e.g. __pycache__/)
        for i in range(1, len(parts) + 1):
            sub_path = "/".join(parts[:i])
            if fnmatch.fnmatch(sub_path, clean_pattern) or fnmatch.fnmatch(parts[i-1], clean_pattern):
                return True
            # Also handle wildcard rules like *.pyc
            if fnmatch.fnmatch(path.name, clean_pattern):
                return True
    return False

def package_project(output_filename="GALXY_Submission.zip"):
    """Packages the workspace into a zip archive excluding gitignored files."""
    root_dir = Path(__file__).parent.resolve()
    gitignore_patterns = load_gitignore_patterns(root_dir)
    
    print(f"[Archive] Packaging project to {output_filename}...")
    print(f"[Archive] Ignoring patterns: {gitignore_patterns}")
    
    zip_count = 0
    ignore_count = 0
    
    with zipfile.ZipFile(root_dir / output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            root_path = Path(root)
            
            # Skip the output zip file itself to prevent recursion
            if root_path == root_dir and output_filename in files:
                files.remove(output_filename)
                
            # Filter directories in-place to prevent os.walk from entering ignored folders
            dirs_to_keep = []
            for d in dirs:
                dir_path = root_path / d
                if should_ignore(dir_path, root_dir, gitignore_patterns):
                    ignore_count += 1
                else:
                    dirs_to_keep.append(d)
            dirs[:] = dirs_to_keep # modifies dirs in-place for os.walk
            
            for file in files:
                file_path = root_path / file
                if should_ignore(file_path, root_dir, gitignore_patterns):
                    ignore_count += 1
                else:
                    zipf.write(file_path, file_path.relative_to(root_dir))
                    zip_count += 1
                    
    print(f"[Archive] Success! Packaged {zip_count} files into {output_filename}.")
    print(f"[Archive] Safely excluded {ignore_count} files/directories matching gitignore rules.")

if __name__ == "__main__":
    package_project()
