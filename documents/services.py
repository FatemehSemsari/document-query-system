from docx import Document as WordDocument
from docx.text.paragraph import Paragraph
from docx.table import Table


def extract_blocks(container):
    texts = []

    for block in container.iter_inner_content():

        if isinstance(block, Paragraph):
            if block.text.strip():
                texts.append(block.text)

        elif isinstance(block, Table):
            for row in block.rows:
                cells = []

                for cell in row.cells:
                    cell_text = '\n'.join(
                        extract_blocks(cell)
                    )
                    cells.append(cell_text)

                texts.append('\t'.join(cells))

    return texts


def extract_docx_text(file):
    file.seek(0)

    try:
        document = WordDocument(file)
        return '\n'.join(
            extract_blocks(document)
        ).strip()

    finally:
        file.seek(0)