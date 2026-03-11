import os
from datetime import datetime


def get_download_path(file_name: str = "document.docx") -> str:
    if os.name == "nt":
        download_path = os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")
    else:
        download_path = os.path.join(os.environ.get("HOME", ""), "Downloads")

    if not download_path or not os.path.isdir(download_path):
        download_path = os.getcwd()

    os.makedirs(download_path, exist_ok=True)
    return os.path.join(download_path, file_name)


def get_timestamped_filename(base_name: str, extension: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"
