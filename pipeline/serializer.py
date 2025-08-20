from openpecha.pecha import Pecha
from pathlib import Path
from openpecha.pecha.serializers import JsonSerializer, SerializerLogicHandler

class TranslationAnnotationSerializer:
    def __init__(self):
        self.DATA_DIR = Path(__file__).parent / "temp_opf"

    def translation_alignment_to_segmentation_annotation(self, opf_id: str):
        opf_path = self.DATA_DIR / opf_id
        pecha = Pecha.from_path(opf_path)

        target = {
            "pecha": pecha,
            "annotation": [
                {
                    "id":"FD4E",
                    "type":"alignment"
                }
                
            ]
        }

        annotation_paths = [
            "0840/alignment-FD4E.json"
        ]
        annotation_id = "FD4E"

        annotation = JsonSerializer().get_annotation(pecha, annotation_paths, annotation_id)

        print(annotation)

if __name__ == "__main__":
    serializer = TranslationAnnotationSerializer()
    serializer.translation_alignment_to_segmentation_annotation(opf_id="IFD8648D1")