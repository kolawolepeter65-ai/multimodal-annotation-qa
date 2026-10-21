import copy
import json
from pathlib import Path
import pytest
from annotation_qa.validator import validate_record, validate_dataset

GOOD = {'id': 'x', 'media_type': 'image', 'width': 100, 'height': 100, 'annotations': [{'id': 'a', 'label': 'cat', 'bbox': [1, 2, 30, 40]}]}
def codes(record, categories=None):
    return [f['code'] for f in validate_record(record, categories)]

def test_valid_item():
    assert codes(GOOD) == []
def test_missing_fields():
    assert 'missing_fields' in codes({'id': 'x'})
def test_invalid_dimensions():
    x = copy.deepcopy(GOOD); x['width'] = 0
    assert 'invalid_dimensions' in codes(x)
def test_out_of_bounds():
    x = copy.deepcopy(GOOD); x['annotations'][0]['bbox'] = [90, 90, 20, 20]
    assert 'out_of_bounds' in codes(x)
def test_empty_box():
    x = copy.deepcopy(GOOD); x['annotations'][0]['bbox'] = [1, 1, 0, 20]
    assert 'empty_bbox' in codes(x)
def test_wrong_box_type():
    x = copy.deepcopy(GOOD); x['annotations'][0]['bbox'] = [0, 0, True, 20]
    assert 'invalid_bbox' in codes(x)
def test_unknown_label():
    assert 'unknown_label' in codes(GOOD, ['person'])
def test_duplicate_annotations():
    x = copy.deepcopy(GOOD); x['annotations'].append(copy.deepcopy(x['annotations'][0]))
    assert 'duplicate_annotation_id' in codes(x)
def test_unlabeled_media():
    x = copy.deepcopy(GOOD); x['annotations'] = []
    assert 'unlabeled_media' in codes(x)
def test_missing_video_metadata():
    x = copy.deepcopy(GOOD); x['media_type'] = 'video_frame'
    assert 'missing_video_id' in codes(x)
    assert 'invalid_frame_index' in codes(x)
def test_duplicate_frames():
    x = copy.deepcopy(GOOD); x.update(media_type='video_frame', video_id='v', frame_index=1)
    y = copy.deepcopy(x); y['id'] = 'y'
    report = validate_dataset({'records': [x, y]})
    assert any(i['code'] == 'duplicate_video_frame' for i in report['records'][1]['findings'])
def test_duplicate_media_ids():
    report = validate_dataset({'records': [GOOD, GOOD]})
    assert report['summary']['errors'] > 0
def test_does_not_mutate_input():
    x = copy.deepcopy(GOOD); before = copy.deepcopy(x)
    validate_record(x)
    assert x == before
def test_missing_dataset():
    with pytest.raises(ValueError): validate_dataset({})
def test_summary_counts():
    report = validate_dataset({'records': [GOOD]})
    assert report['summary']['passed'] and report['summary']['annotations'] == 1
def test_sample_dataset():
    cases = json.loads((Path(__file__).parents[1] / 'data' / 'sample_dataset.json').read_text())
    report = validate_dataset(cases)
    assert report['summary']['media_items'] == 4
    assert report['summary']['errors'] == 1
    assert report['summary']['warnings'] == 1
