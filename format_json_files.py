import os
import json
from tqdm import tqdm


def main():
    # Looks inside ../Docket-Info/json-files/*.json
    folder = os.path.join('Docket-Info', 'json-files')
    for json_file in tqdm([os.path.join(folder, x) for x in os.listdir(folder)]):
        with open(json_file, 'r') as f:
            json_data = json.load(f)
            f.close()

        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    main()
