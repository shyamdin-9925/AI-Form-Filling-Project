import zipfile
import os


def create_zip(file_paths: list, output_path: str) -> str:
    """
    Bundles all compressed documents into a single ZIP file.
    Input:  list of file paths, output zip path
    Output: path to generated ZIP file
    """
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            if os.path.exists(file_path):
                # Add file to zip using just the filename not full path
                zipf.write(file_path, os.path.basename(file_path))
                print(f"Added to ZIP: {file_path}")
            else:
                print(f"File not found, skipping: {file_path}")

    print(f"ZIP created: {output_path}")
    return output_path

