# Handwritten Maths Formula

FastAPI + React application for converting uploaded handwritten mathematical expression images into LaTeX.

## Active OCR Architecture

The production prediction path uses Pix2Tex (`pix2tex.cli.LatexOCR`) as the primary OCR engine:

`upload -> validation -> Pix2Tex-compatible preprocessing -> Pix2Tex OCR -> LaTeX response -> KaTeX rendering -> history`

Legacy YOLO symbol detection, expression parsing, AST generation, and LaTeX generation files remain in the repository for research/reference, but `/api/v1/predict`, `/api/v1/expressions/recognize`, and `/api/v1/model/status` no longer call them.

## Model Lifecycle

Pix2Tex is loaded once during FastAPI startup through `app.services.pix2tex_service.Pix2TexOCRService`. Startup fails fast if the model cannot load. A singleton instance is reused for every request, and inference is protected by a lock for thread-safe access.

Health is available at:

- `/health`
- `/api/v1/model/status`

Containers persist Pix2Tex/Hugging Face cache data in the `pix2tex_cache` Docker volume to avoid repeated downloads after initial setup. Uploaded images are persisted in `backend_uploads`.

## Preprocessing Policy

Pix2Tex receives a PIL image, not the previous YOLO tensor format. The active OCR preprocessing keeps:

- Grayscale conversion, because math meaning is stroke intensity rather than color.
- Light median denoising, because it removes isolated specks while preserving edges.
- Autocontrast, because it improves faint handwriting without hard binarization.

The active OCR path skips adaptive thresholding, fixed 640x640 padding, and float normalization because those steps were YOLO-oriented and can degrade thin bars, dots, roots, brackets, and matrix layouts.

## API Response

Prediction responses include generated LaTeX, image path, prediction id, UTC timestamp, total time, preprocessing time, OCR time, confidence, and confidence source. Pix2Tex does not currently expose calibrated confidence, so successful non-empty OCR responses use a documented placeholder confidence of `0.80` with `confidence_source=placeholder_success_default`.

## Deployment

Run the full stack:

```bash
docker compose up --build
```

Backend environment variables:

- `DATABASE_URL`: SQLAlchemy database URL.
- `HF_HOME`: Hugging Face/Pix2Tex model cache path.
- `XDG_CACHE_HOME`: general model cache path.
- `BACKEND_CORS_ORIGINS`: comma-separated or JSON list of allowed origins.

## Validation Notes

Automated tests cover startup health, Pix2Tex service reuse, upload validation flow, prediction response shape, and history-compatible persistence. Recognition quality should still be validated with real handwritten samples for fractions, roots, integrals, sums, matrices, Greek symbols, and multi-line expressions before production release.
