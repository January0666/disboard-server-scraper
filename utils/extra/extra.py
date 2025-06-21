import os


def save_to_file(data, keyword: str,timestamp : str):
    """
    Save data to a timestamped file inside a keyword-based folder.
    :param data: Data to be saved.
    :param keyword: Keyword used to name the folder and file.
    """
    try:
        output_dir = f"data/output/{keyword}"
        os.makedirs(output_dir, exist_ok=True)

        
        file_path = os.path.join(output_dir, f"{timestamp}.txt")

        with open(file_path, "a", encoding="utf-8") as file:
            file.write(data + "\n")

    except Exception as e:
        print(f"Error saving data to file: {e}")
