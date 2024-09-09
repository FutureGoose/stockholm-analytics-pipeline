import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from tqdm import tqdm

def run_bq_command(command: str) -> Optional[Dict[str, Any]]:
    """
    Executes a bq command and returns the output as a JSON object.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(result.stderr)
            return None
        return json.loads(result.stdout)
    except subprocess.SubprocessError as e:
        print(f"Subprocess error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None


def save_json_to_file(data: Dict[str, Any], file_path: Path) -> None:
    """
    Saves JSON data to a specified file.
    """
    try:
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)
    except IOError as e:
        print(f"IO error when writing to file {file_path}: {e}")


def process_dataset(dataset: str, output_dir: Path) -> None:
    """
    Processes a dataset by listing its tables and saving detailed information for each table to a JSON file.
    """
    tables = run_bq_command(f"bq ls --format=prettyjson {dataset}")
    if tables is None:
        return
    
    dataset_dir = output_dir / dataset
    try:
        dataset_dir.mkdir(parents=True, exist_ok=True)
    except IOError as e:
        print(f"IO error when creating directory {dataset_dir}: {e}")
        return
    
    for table in tqdm(tables, desc=f"Processing tables in {dataset}", leave=False):
        table_id = table['tableReference']['tableId']
        table_info = run_bq_command(f"bq show --format=prettyjson {dataset}.{table_id}")
        if table_info is not None:
            file_path = dataset_dir / f"{table_id}.json"
            save_json_to_file(table_info, file_path)


def list_datasets() -> List[str]:
    """
    Lists all datasets in the project.
    """
    datasets = run_bq_command("bq ls --format=prettyjson")
    if datasets is None:
        return []
    return [dataset['datasetReference']['datasetId'] for dataset in datasets]


def main():
    output_dir = Path("database_schemas")
    try:
        output_dir.mkdir(exist_ok=True)
    except IOError as e:
        print(f"IO error when creating directory {output_dir}: {e}")
        return

    datasets = list_datasets()
    for dataset in tqdm(datasets, desc="Processing datasets"):
        process_dataset(dataset, output_dir)

if __name__ == "__main__":
    main()