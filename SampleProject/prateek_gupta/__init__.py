from pathlib import Path


project_dir=str(Path(__file__).resolve().parent.parent).replace("\\", "/")
if project_dir[-1]!="/":
    project_dir+="/"
console_logs=True