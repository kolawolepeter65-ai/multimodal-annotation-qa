"""Transparent dataset QA for image and video bounding-box labels."""
from collections import Counter

REQUIRED = {'id', 'media_type', 'width', 'height', 'annotations'}

def issue(code, severity, message, annotation_id=None):
    out = {'code': code, 'severity': severity, 'message': message}
    if annotation_id is not None:
        out['annotation_id'] = annotation_id
    return out

def validate_record(record, categories=None):
    """Return audit findings; never mutate user annotations."""
    findings = []
    if not isinstance(record, dict):
        return [issue('invalid_record', 'error', 'Media record must be an object')]
    if not REQUIRED.issubset(record):
        return [issue('missing_fields', 'error', 'Required media fields are missing')]
    if not isinstance(record['id'], str) or not record['id']:
        findings.append(issue('invalid_id', 'error', 'Media id must be nonempty text'))
    if record['media_type'] not in ('image', 'video_frame'):
        findings.append(issue('invalid_media_type', 'error', 'Use image or video_frame'))
    width, height = record['width'], record['height']
    if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
        return findings + [issue('invalid_dimensions', 'error', 'Dimensions must be positive integers')]
    if record['media_type'] == 'video_frame':
        if not isinstance(record.get('video_id'), str) or not record['video_id']:
            findings.append(issue('missing_video_id', 'error', 'Video frames require video_id'))
        if type(record.get('frame_index')) is not int or record['frame_index'] < 0:
            findings.append(issue('invalid_frame_index', 'error', 'Video frames need nonnegative integer frame_index'))
    if not isinstance(record['annotations'], list):
        return findings + [issue('invalid_annotations', 'error', 'Annotations must be a list')]
    if not record['annotations']:
        findings.append(issue('unlabeled_media', 'warning', 'No annotations on this media item'))
    seen = set()
    for i, ann in enumerate(record['annotations']):
        fallback = str(i)
        if not isinstance(ann, dict):
            findings.append(issue('invalid_annotation', 'error', 'Annotation must be an object', fallback))
            continue
        aid = ann.get('id', fallback)
        if not isinstance(aid, str) or not aid:
            findings.append(issue('invalid_annotation_id', 'error', 'Annotation id must be nonempty text', fallback))
            aid = fallback
        if aid in seen:
            findings.append(issue('duplicate_annotation_id', 'error', 'Duplicate annotation id on this media item', aid))
        seen.add(aid)
        label = ann.get('label')
        if not isinstance(label, str) or not label.strip():
            findings.append(issue('missing_label', 'error', 'Annotation must have a label', aid))
        elif categories is not None and label not in categories:
            findings.append(issue('unknown_label', 'error', 'Label is not in category list', aid))
        box = ann.get('bbox')
        if not isinstance(box, list) or len(box) != 4 or any(type(x) not in (int, float) for x in box):
            findings.append(issue('invalid_bbox', 'error', 'bbox must be [x,y,width,height] with numeric values', aid))
            continue
        x, y, w, h = box
        if w <= 0 or h <= 0:
            findings.append(issue('empty_bbox', 'error', 'Bounding-box width and height must be positive', aid))
        if x < 0 or y < 0 or x + w > width or y + h > height:
            findings.append(issue('out_of_bounds', 'error', 'Bounding box exceeds image dimensions', aid))
        if w > 0 and h > 0 and w * h < 0.0001 * width * height:
            findings.append(issue('tiny_bbox', 'warning', 'Bounding box covers less than 0.01% of frame', aid))
    return findings

def validate_dataset(data):
    if not isinstance(data, dict) or not isinstance(data.get('records'), list):
        raise ValueError('Dataset requires a records list')
    categories = data.get('categories')
    if categories is not None and (not isinstance(categories, list) or any(not isinstance(c, str) for c in categories)):
        raise ValueError('categories must be a list of strings')
    report = []
    keys = set()
    media_ids = set()
    label_counts = Counter()
    for i, record in enumerate(data['records']):
        item_id = record.get('id', f'item-{i}') if isinstance(record, dict) else f'item-{i}'
        findings = validate_record(record, categories)
        if isinstance(record, dict):
            if item_id in media_ids:
                findings.append(issue('duplicate_media_id', 'error', 'Media id repeated in dataset'))
            media_ids.add(item_id)
            if record.get('media_type') == 'video_frame':
                key = (record.get('video_id'), record.get('frame_index'))
                if key in keys:
                    findings.append(issue('duplicate_video_frame', 'error', 'Duplicate video and frame index'))
                keys.add(key)
            for ann in record.get('annotations', []) if isinstance(record.get('annotations'), list) else []:
                if isinstance(ann, dict) and isinstance(ann.get('label'), str) and ann['label'].strip():
                    label_counts[ann['label']] += 1
        report.append({'media_id': str(item_id), 'findings': findings})
    errors = sum(x['severity'] == 'error' for r in report for x in r['findings'])
    warnings = sum(x['severity'] == 'warning' for r in report for x in r['findings'])
    return {'summary': {'media_items': len(data['records']), 'annotations': sum(label_counts.values()), 'errors': errors, 'warnings': warnings, 'passed': errors == 0}, 'label_counts': dict(sorted(label_counts.items())), 'records': report}
