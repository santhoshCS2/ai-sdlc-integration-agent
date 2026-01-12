import os
import tempfile

# Central store for tracking generated agent outputs for download
# Key: file_id (UUID), Value: absolute_path
generated_files = {}

def get_report_path(file_id: str) -> str:
    return generated_files.get(file_id)

def register_report(file_id: str, path: str):
    generated_files[file_id] = path
