from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def make_sheet(folder: Path, output: Path) -> None:
    paths = sorted(folder.glob("page-*"))
    cell_w, cell_h = 430, 265
    columns = 3
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=20)
    for index, path in enumerate(paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((cell_w - 20, cell_h - 38))
        x = (index % columns) * cell_w + (cell_w - image.width) // 2
        y = (index // columns) * cell_h + 30
        sheet.paste(image, (x, y))
        draw.text(((index % columns) * cell_w + 10, (index // columns) * cell_h + 5), path.stem, fill="black", font=font)
    output.parent.mkdir(exist_ok=True)
    sheet.save(output, quality=90)


def main() -> None:
    root = Path(__file__).parent / "extracted_pages"
    output_root = Path(__file__).parent / "contact_sheets"
    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        make_sheet(folder, output_root / f"{folder.name}.jpg")


if __name__ == "__main__":
    main()
