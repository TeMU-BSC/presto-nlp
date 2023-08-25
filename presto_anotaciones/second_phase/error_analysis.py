# Script to compute error analysis on annotations for the second phase (different from the first phase)
from argparse import ArgumentParser
import jsonlines
import pandas as pd
from collections import defaultdict, Counter


def obs_agreement(ann):
    """Count the number of common labels"""
    num_pre_ann_labels = len(set(ann["pre_annotation"]))
    if num_pre_ann_labels == 0:
        obs_agreement = 0
    else:
        obs_agreement = (
            len(set(ann["pre_annotation"]).intersection(set(ann["all"])))
            / num_pre_ann_labels
        )
        obs_agreement *= 100

    return obs_agreement
    # labels = []
    # for key in ann.keys():
    #     if key != "text":
    #         labels.extend(ann[key])
    # if labels:
    #     obs_agreement = Counter(labels).most_common(1)[0][1]
    # else:
    #     print(f"Empty annotation: {ann}")
    #     obs_agreement = ""
    # return obs_agreement


if __name__ == "__main__":
    file_ann = "./presto_annotation.jsonl"
    for level in ["distortion", "types"]:
        file_errors = f"./errors_{level}.csv"

        # add text and annotation labels for pre-annotations and all the annotators
        table_rows = defaultdict()
        with jsonlines.open(file_ann) as pre_ann:
            for ann in pre_ann:
                table_row = defaultdict()
                table_row["text"] = ann["text"]
                # table_row['id'] = ann['id']
                if level == "types":
                    table_row["pre_annotation"] = [
                        ann.lower() for ann in ann["pre-ann-category"][level]
                    ]
                else:
                    table_row["pre_annotation"] = [ann["pre-ann-category"][level]]
                table_rows[ann["id"]] = table_row

        with jsonlines.open(file_ann) as ann_level:
            for ann in ann_level:
                ann_name = "all"
                if level == "types":
                    table_rows[ann["id"]][ann_name] = ann["types"]
                else:
                    table_rows[ann["id"]][ann_name] = ann["accept"]

        for ann in table_rows.values():
            agreement = obs_agreement(ann)
            ann.update({"agreement %": agreement})

        table_rows = dict(table_rows)
        df = pd.DataFrame.from_records(
            list(table_rows.values()), index=list(table_rows.keys())
        )
        df.to_csv(file_errors)
