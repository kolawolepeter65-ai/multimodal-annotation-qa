"""Streamlit demo of a transparent multimodal annotation quality validator."""
import json
from pathlib import Path
import streamlit as st
from annotation_qa.validator import validate_dataset

st.set_page_config(page_title='Multimodal Annotation QA', page_icon='🎞️', layout='wide')
st.title('🎞️ Multimodal Annotation QA')
st.caption('Validate image and video-frame bounding boxes, label taxonomies, and annotation structure.')
st.info('This is a deterministic dataset validator, not an AI vision model. Example data is synthetic.')
example = (Path(__file__).parent / 'data' / 'sample_dataset.json').read_text(encoding='utf-8')
upload = st.file_uploader('Upload your annotation dataset (JSON)', type=['json'])
if upload:
    try:
        text = upload.getvalue().decode('utf-8')
    except UnicodeDecodeError:
        st.error('File must contain UTF-8 JSON.')
        st.stop()
else:
    text = example
source_text = st.text_area('Dataset JSON (editable)', value=text, height=300)
if st.button('Run annotation QA', type='primary'):
    try:
        dataset = json.loads(source_text)
        report = validate_dataset(dataset)
    except (ValueError, TypeError) as e:
        st.error(f'Invalid dataset: {e}')
    else:
        a, b, c, d = st.columns(4)
        a.metric('Media items', report['summary']['media_items'])
        b.metric('Annotations', report['summary']['annotations'])
        c.metric('Errors', report['summary']['errors'])
        d.metric('Warnings', report['summary']['warnings'])
        st.success('No structural errors found.') if report['summary']['passed'] else st.warning('Structural errors found.')
        rows = [{'Media': r['media_id'], 'Severity': f['severity'], 'Code': f['code'], 'Annotation': f.get('annotation_id', ''), 'Details': f['message']} for r in report['records'] for f in r['findings']]
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.write('No findings.')
        st.subheader('Label distribution')
        if report['label_counts']:
            st.bar_chart(report['label_counts'])
        st.download_button('Download QA report', json.dumps(report, indent=2), file_name='annotation_qa_report.json', mime='application/json')
st.markdown('[GitHub source code](https://github.com/kolawolepeter65-ai/multimodal-annotation-qa)')
