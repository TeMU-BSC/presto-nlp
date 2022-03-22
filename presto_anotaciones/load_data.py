
import pandas
from tqdm import tqdm
import csv
import sys
import os
import jsonlines


def load_data(input_file):
    assert os.path.splitext(input_file)[1] == '.csv', ValueError(
        "Please use a .csv file!")
    df = pandas.read_csv(input_file, header=0)
    data = []

    # Parse pandas info (from csv)
    for index in tqdm(df.index):
        row = df.loc[index]
        try:
            n = int(row["Nº"])
        except:
            continue
        if n in range(1, 21):
            columns2id = {
                "Texto con distorsión cognitiva": "d",
                "Pensamiento alternativo": "da",
                "Construcciones tricky": "t"
            }
            for column, letter in columns2id.items():
                text_content = row[column]

                line = {
                    "ground-thruth": f"{letter}", "text": text_content}
                data.append(line)

    output_file = os.path.join(os.path.dirname(
        input_file), os.path.splitext(input_file)[0] + '.jsonl')

    with jsonlines.open(output_file, "a") as writer:
        for line in data:
            writer.write(line)


if __name__ == '__main__':
    input_file = sys.argv[1]
    load_data(input_file)
