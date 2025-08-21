from pathlib import Path
from openpecha.pecha import Pecha
from stam import AnnotationStore
from openpecha.pecha.layer import (
    AnnotationType,
    get_annotation_group_type,
    get_annotation_type
)
from openpecha.pecha.annotations import AlignmentAnnotation, Span
import re


def _get_ann_type(layer_path: str):
    layer_name = layer_path.split("/")[1]
    ann_name = layer_name.split("-")[0]
    return get_annotation_type(ann_name)


def get_annotations(pecha, annotation_paths):
    annotations = {}
    for annotation_path in annotation_paths:
        ann_store = AnnotationStore(file=str(pecha.layer_path / annotation_path))
        ann_type = _get_ann_type(annotation_path)
        annotations[ann_type.value] = to_dict(ann_store, ann_type)
    return annotations


def to_dict(ann_store: AnnotationStore, ann_type: AnnotationType):
    ann_group = get_annotation_group_type(ann_type)
    anns = []

    for ann in ann_store:
        ann_data = {}
        for data in ann:
            k, v = data.key().id(), data.value().get()
            if k != ann_group.value:
                ann_data[k] = v
        curr_ann = {
            "id": ann.id(),
            "Span": {
                "start": ann.offset().begin().value(),
                "end": ann.offset().end().value(),
            },
            **ann_data,
        }

        anns.append(curr_ann)

    return anns

def get_annotation_paths(pecha: Pecha, annotations: list[dict]):
    def get_annotation_names(annotations: list[dict]):
        annotation_filenames = []
        for annotation in annotations:
            if annotation['type'] == 'alignment':
                annotation_filenames.append(annotation['type'] + "-" + annotation["id"])
            elif annotation['type'] == 'segmentation':
                annotation_filenames.append(annotation['type'] + "-" + annotation["id"])
            else:
                continue
        return annotation_filenames
    
    annotation_paths = []
    annotation_filenames = get_annotation_names(annotations)

    for base_name in pecha.bases.keys():
        for path in Path(pecha.layer_path/base_name).iterdir():
            if path.stem in annotation_filenames:
                annotation_paths.append("/".join(path.parts[-2:]))
    return annotation_paths


def convert_to_new_format(annotations_dict, language):
    if language != 'bo':
        for ann_type, ann_list in annotations_dict.items():
            sorted_anns = sorted(ann_list, key=lambda x: x['Span']['start'])
            
            for i, ann in enumerate(sorted_anns):
                ann['index'] = i + 1
                if 'root_idx_mapping' in ann:
                    ann['alignment_index'] = [ann['root_idx_mapping']]
                    del ann['root_idx_mapping']
            
            annotations_dict[ann_type] = sorted_anns
    else:
        for ann_type, ann_list in annotations_dict.items():
            sorted_anns = sorted(ann_list, key=lambda x: x['Span']['start'])
            for i, ann in enumerate(sorted_anns):
                ann['index'] = i + 1
                ann['alignment_index'] = []
            annotations_dict[ann_type] = sorted_anns
    
    return annotations_dict


def update_alignment(config, language: str):
    pecha_path = Path(config['pecha_path'])
    annotation_dict = config['annotations']

    pecha = Pecha.from_path(pecha_path)
    
    annotation_paths = get_annotation_paths(pecha, annotation_dict)
    
    annotations = get_annotations(pecha, annotation_paths)
    
    new_annotations = convert_to_new_format(annotations, language) # You have to pass the language of the pecha

    return new_annotations


def scan_opf_directory(dir_name: str) -> list[dict]:

    opf_root_path: Path = Path(f"pipeline/{dir_name}")
    
    pecha_configs = []
    
    if not opf_root_path.is_absolute():
        opf_root_path = Path.cwd() / opf_root_path
    
    
            
    for pecha_dir in opf_root_path.iterdir():
        if not pecha_dir.is_dir():
            continue
            
        try:
            pecha_path = str(pecha_dir.relative_to(Path.cwd()))
        except ValueError:
            pecha_path = str(pecha_dir.relative_to(opf_root_path.parent))
        
        base_dir = pecha_dir / "base"
        layers_dir = pecha_dir / "layers"
        
        if not (base_dir.exists() and layers_dir.exists()):
            continue
        
        annotations = []
        
        for base_subdir in layers_dir.iterdir():
            if not base_subdir.is_dir():
                continue
                
            for annotation_file in base_subdir.iterdir():
                if annotation_file.suffix == '.json':
                    filename_parts = annotation_file.stem.split('-', 1)
                    if len(filename_parts) == 2:
                        ann_type, ann_id = filename_parts
                        annotations.append({
                            'id': ann_id,
                            'type': ann_type
                        })
        
        
        pecha_config = {
            'pecha_path': pecha_path,
            'annotations': annotations
        }
        
        pecha_configs.append(pecha_config)
    
    return pecha_configs

if __name__ == "__main__":
    pecha_configs = scan_opf_directory()
    for config in pecha_configs:
        update_alignment(config)