from pathlib import Path

from pypdf import PdfReader


def main() -> None:
    source_dir = Path(__file__).parent
    output_root = source_dir / "extracted_pages"
    output_root.mkdir(exist_ok=True)

    for pdf_path in sorted(source_dir.glob("*.pdf")):
        reader = PdfReader(str(pdf_path))
        pdf_output = output_root / pdf_path.stem
        pdf_output.mkdir(exist_ok=True)
        for page_number, page in enumerate(reader.pages, start=1):
            images = list(page.images)
            if not images:
                continue
            # These lecture PDFs are image-based. Keep the largest image on each
            # page, which is the full slide/page rather than a tiny decoration.
            largest = max(images, key=lambda image: len(image.data))
            suffix = Path(largest.name).suffix or ".png"
            target = pdf_output / f"page-{page_number:02d}{suffix}"
            target.write_bytes(largest.data)
            print(target)


if __name__ == "__main__":
    main()
