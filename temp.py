from openpecha.pecha.serializers.json import JsonSerializer
from pathlib import Path
from openpecha.pecha import Pecha

opf_path = Path("_GQyscRHEaSM9td8")

opf = Pecha.from_path(opf_path.resolve())

annotation_paths = ["008D/alignment-QsnEvKCo01tZaQ3j.json"]

annotation_id = "QsnEvKCo01tZaQ3j"

serializer = JsonSerializer()
annotation = serializer.get_annotation(pecha=opf, annotation_paths=annotation_paths, annotation_id=annotation_id)

import json

# Determine the output path: same directory as the annotation file
output_dir = Path(annotation_paths[0]).parent
output_path = output_dir / f"{annotation_id}_output.json"

# Ensure the output directory exists before writing the file
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(annotation, f, ensure_ascii=False, indent=2)



