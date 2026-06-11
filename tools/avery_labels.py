from __future__ import annotations

from pathlib import Path
import argparse
import html
import webbrowser


# -------------------------------------------------------------------
# Avery template settings
# Adjust margins/gaps slightly if your printer needs calibration
# -------------------------------------------------------------------
TEMPLATES = {
    "5162": {
        "page_width": 8.5,
        "page_height": 11.0,
        "columns": 2,
        "rows": 7,
        "label_width": 4.0,
        "label_height": 1.333333,  # 1-1/3"
        "margin_top": 0.5,
        "margin_left": 0.15625,
        "column_gap": 0.1875,
        "row_gap": 0.0,
        "sheet_name": "Avery 5162",
    },
    "5263": {
        "page_width": 8.5,
        "page_height": 11.0,
        "columns": 2,
        "rows": 5,
        "label_width": 4.0,
        "label_height": 2.0,
        "margin_top": 0.5,
        "margin_left": 0.15625,
        "column_gap": 0.1875,
        "row_gap": 0.0,
        "sheet_name": "Avery 5263",
    },
}


def inch(value: float) -> str:
    """
    Format a numeric inch value for CSS.
    """
    return f"{value:.5f}in"


def chunked(seq: list[Path], size: int) -> list[list[Path]]:
    """
    Split a list into fixed-size chunks.
    """
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def build_html(
    images: list[Path],
    template_key: str,
    image_root: Path,
    title: str = "PackIt QR Labels",
    label_padding_in: float = 0.03,
) -> str:
    """
    Build printable HTML for Avery-style label sheets.
    """
    if template_key not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_key}")

    t = TEMPLATES[template_key]
    labels_per_page = t["columns"] * t["rows"]
    pages = chunked(images, labels_per_page)

    page_blocks: list[str] = []

    for page_images in pages:
        cells: list[str] = []

        for i in range(labels_per_page):
            if i < len(page_images):
                img = page_images[i]
                rel_src = img.relative_to(image_root).as_posix()
                alt_text = html.escape(img.stem)

                cell = f"""
                <div class="label">
                  <div class="label-inner">
                    <img src="{html.escape(rel_src)}" alt="{alt_text}">
                  </div>
                </div>
                """
            else:
                cell = """
                <div class="label">
                  <div class="label-inner empty"></div>
                </div>
                """
            cells.append(cell)

        page_blocks.append(f"""
        <section class="sheet">
          {''.join(cells)}
        </section>
        """)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)} - {html.escape(t["sheet_name"])}</title>
  <style>
    @page {{
      size: {inch(t["page_width"])} {inch(t["page_height"])}; 
      margin: 0;
    }}

    * {{
      box-sizing: border-box;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      background: white;
      font-family: Arial, Helvetica, sans-serif;
    }}

    body {{
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}

    .sheet {{
      width: {inch(t["page_width"])};
      height: {inch(t["page_height"])};
      padding-top: {inch(t["margin_top"])};
      padding-left: {inch(t["margin_left"])};
      display: grid;
      grid-template-columns: repeat({t["columns"]}, {inch(t["label_width"])});
      grid-template-rows: repeat({t["rows"]}, {inch(t["label_height"])});
      column-gap: {inch(t["column_gap"])};
      row-gap: {inch(t["row_gap"])};
      page-break-after: always;
      overflow: hidden;
    }}

    .sheet:last-child {{
      page-break-after: auto;
    }}

    .label {{
      width: {inch(t["label_width"])};
      height: {inch(t["label_height"])};
      padding: {inch(label_padding_in)};
      overflow: hidden;
    }}

    .label-inner {{
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }}

    .label img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      object-position: center;
      display: block;
    }}

    .empty {{
      border: none;
    }}

    @media screen {{
      body {{
        background: #eee;
        padding: 12px;
      }}

      .sheet {{
        margin: 0 auto 16px auto;
        background: white;
        box-shadow: 0 0 6px rgba(0,0,0,0.15);
      }}
    }}
  </style>
</head>
<body>
  {''.join(page_blocks)}
</body>
</html>
"""


def resolve_input_paths(
    room_abbr: str | None,
    pdf_folder: str | None,
    template: str,
) -> tuple[Path, Path, str]:
    """
    Resolve the source PNG folder, output HTML path, and title.

    Exactly one of room_abbr or pdf_folder must be provided.
    """
    if room_abbr:
        room = room_abbr.upper().strip()
        qr_dir = Path(f"D:/MindItArchive/packit/qrcodes/{room}")
        output_html = Path(
            f"D:/MindItArchive/packit/qrcodes/{room}/{room}_{template}.html"
        )
        title = f"PackIt QR Labels - {room}"
        return qr_dir, output_html, title

    if pdf_folder:
        qr_dir = Path(pdf_folder).expanduser().resolve()
        output_html = qr_dir / f"{qr_dir.name}_{template}.html"
        title = f"PDF QR Labels - {qr_dir.name}"
        return qr_dir, output_html, title

    raise ValueError("Either room_abbr or pdf_folder must be provided.")


def main() -> None:
    """
    Build a printable Avery label HTML file from QR code PNG images.
    """
    parser = argparse.ArgumentParser()

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--room-abbr",
        type=str,
        help="Room abbreviation, example: LR",
    )
    source_group.add_argument(
        "--pdf-folder",
        type=str,
        help="Folder containing PDF QR code PNG files.",
    )

    parser.add_argument(
        "--template",
        default="5263",
        choices=TEMPLATES.keys(),
        help="Avery template number",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the generated HTML in the default browser.",
    )

    args = parser.parse_args()

    qr_dir, output_html, title = resolve_input_paths(
        room_abbr=args.room_abbr,
        pdf_folder=args.pdf_folder,
        template=args.template,
    )

    if not qr_dir.exists():
        raise SystemExit(f"Input folder does not exist: {qr_dir}")

    images = sorted(qr_dir.glob("*.png"))
    if not images:
        raise SystemExit(f"No PNG files found in: {qr_dir}")

    html_text = build_html(
        images=images,
        template_key=args.template,
        image_root=qr_dir,
        title=title,
        label_padding_in=0.03,
    )

    output_html.write_text(html_text, encoding="utf-8")

    if args.open_browser:
        webbrowser.open(output_html.resolve().as_uri())

    print(f"Wrote: {output_html.resolve()}")
    print(f"Source folder: {qr_dir}")
    print(f"Images: {len(images)}")
    print(f"Template: {args.template}")
    print(f"Title: {title}")


if __name__ == "__main__":
    main()
