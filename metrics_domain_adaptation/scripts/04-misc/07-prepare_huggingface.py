"""
- Adds references together
- Fixes locale information
- Updates the field names
"""

# add references

import glob
import json
import re
import collections

def annotator_id(s, lang1, lang2):
    assert s is not None
    if type(s) == int:
        return s
    else:
        return str(s) + "/" + lang1 + lang2

RE_4LANG_TO_2LANG = re.compile(r"(..)..-(..)..")

# maps (src, langs) to reference
srcl_to_ref = collections.defaultdict(list)

data_out_ref = []
data_out_sys = []

# load references
for file in glob.glob(
    "data/v2/target/main_phase/round_two/*/reference*.json", recursive=True
):
    for line in json.load(open(file, "r", encoding='utf-8-sig')):
        # print(line["MT_Engine"])
        line = {
            "src": line["source"],
            "tgt": line["target"],
            "ref": [],
            "system": "reference_1" if line["MT_Engine"] == "reference_r1" else "reference_2",
            "lang_src": line["source_locale"][:2],
            "lang_tgt": line["target_locale"][:2],
            "annotator": annotator_id(line["Annotator_ID"], line["source_locale"][:2], line["target_locale"][:2]),
            "errors_src": line["source_errors"],
            "errors_tgt": line["target_errors"],
            "doc_id": line["DOC_ID"],
        }
        data_out_ref.append(line)
        srcl_to_ref[(line["src"], line["lang_src"], line["lang_tgt"])].append(line["tgt"])


# load systems
for file in glob.glob(
    "data/v2/target/main_phase/round_two/*/*.json", recursive=True
):
    # skip references
    if "reference" in file:
        continue
    for line in json.load(open(file, "r", encoding='utf-8-sig')):
        # print()
        line = {
            "src": line["source"],
            "tgt": line["target"],
            "ref": srcl_to_ref[(line["source"], line["source_locale"][:2], line["target_locale"][:2])],
            "system": line["MT_Engine"],
            "lang_src": line["source_locale"][:2],
            "lang_tgt": line["target_locale"][:2],
            "annotator": annotator_id(line["Annotator_ID"], line["source_locale"][:2], line["target_locale"][:2]),
            "errors_src": line["source_errors"],
            "errors_tgt": line["target_errors"],
            "doc_id": line["DOC_ID"],
        }
        data_out_sys.append(line)

print(len(srcl_to_ref), "sources")
print(len(data_out_ref), "references")
print(len(data_out_sys), "targets")

docid_splits = json.load(open("data/doc_id_splits.json", "r"))


data_out_dev = [
    line
    for line in data_out_sys + data_out_ref
    if (
        line["lang_src"]+"-"+line["lang_tgt"] in docid_splits and
        line["doc_id"] in docid_splits[line["lang_src"]+"-"+line["lang_tgt"]]["dev"]
    )
]
# default to test
data_out_test = [
    line
    for line in data_out_sys + data_out_ref
    if (
        line["lang_src"]+"-"+line["lang_tgt"] not in docid_splits or
        line["doc_id"] not in docid_splits[line["lang_src"]+"-"+line["lang_tgt"]]["dev"]
    )
]

data_out_dev.sort(key=lambda x: x["lang_tgt"] == "de", reverse=True)
data_out_test.sort(key=lambda x: x["lang_tgt"] == "de", reverse=True)

print(len(data_out_dev), "dev")
print(len(data_out_test), "test")
with open("computed/dev.jsonl", "w") as f:
    f.write("\n".join([json.dumps(x, ensure_ascii=False) for x in data_out_dev]))
with open("computed/test.jsonl", "w") as f:
    f.write("\n".join([json.dumps(x, ensure_ascii=False) for x in data_out_test]))