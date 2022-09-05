# Deduplicate annotations in case there are any.
import jsonlines
import sys

# annotations_file = sys.argv[1]
annotations_file = sys.argv[1]
annotations_dedup = []
annotations_dup = []
# tuple to identify seen ids and _annotator_id examples
seen_ids_annotator_ids = []
with jsonlines.open(annotations_file) as reader:
    for ann in reader:
        id_annotator_id = f"{ann['id']}-{ann['_annotator_id']}"
        if not id_annotator_id in seen_ids_annotator_ids:
            annotations_dedup.append(ann)
            seen_ids_annotator_ids.append(id_annotator_id)
        else:
            annotations_dup.append(ann)

print(f"found duplicated annotations: {len(annotations_dup)}")
annotations_dedup_file = annotations_file.replace('.json', '.dedup.json')
with jsonlines.open(annotations_dedup_file, mode='w') as writer:
    writer.write_all(annotations_dedup)
print(f"write deduplicated annotations to file: {annotations_dedup_file}")

