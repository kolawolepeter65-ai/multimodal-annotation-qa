# Multimodal Annotation QA

[![Python Tests](https://github.com/kolawolepeter65-ai/multimodal-annotation-qa/actions/workflows/tests.yml/badge.svg)](https://github.com/kolawolepeter65-ai/multimodal-annotation-qa/actions/workflows/tests.yml)

An image and video-frame bounding-box annotation quality assurance tool, with reproducible validations, label statistics, and auditable errors.

## Features
- Detect invalid or out-of-bounds bounding boxes, duplicate media/annotation IDs and duplicate video frames
- Flag missing labels, unknown categories and unannotated media
- Export a JSON audit report in an interactive Streamlit app
- Synthetic example dataset, 16 pytest tests, Dockerfile, and GitHub Actions

**Scope:** This deterministic validator audits metadata and box geometry; it is not a computer-vision model and does not inspect image pixels. No confidential training data is included.

## Run
```bash
python -m pip install -e '.[test]'
python -m pytest -q
streamlit run app.py
```

## Live demo
Deploy via [Streamlit Community Cloud](https://share.streamlit.io/) using repository `kolawolepeter65-ai/multimodal-annotation-qa`, branch `main`, entry file `app.py`. Add the public URL after deploying.

## Docker
```bash
docker build -t multimodal-annotation-qa .
docker run --rm multimodal-annotation-qa
```

## Dataset format
Supply JSON with `records` and optional `categories`. Each record has `id`, `media_type` (`image` or `video_frame`), positive integer `width` and `height`, and `annotations`. Video frames also require `video_id` and `frame_index`. Annotations use a label and an absolute pixel-space bounding box `[x, y, width, height]`.

## Author
Kolawole Peter Olusola · [Portfolio](https://techbykhay.site/) · [LinkedIn](https://www.linkedin.com/in/kolawole-peter-olusola/)
