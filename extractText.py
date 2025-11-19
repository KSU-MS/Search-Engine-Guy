from pdf2image import convert_from_path
import pytesseract
import filetype
import pymupdf4llm
from pdf2image.pdf2image import pdfinfo_from_path

def main(file, format = "text"):
    kind = filetype.guess(file)
    print(f"file '{file}' is a '{kind.extension}' file")

    file_contents = []
    
    if kind.extension == "pdf":
        if format == "text":
            info = pdfinfo_from_path(file)
            total_pages = info["Pages"]

            for page_number in range(1, total_pages + 1):
                page = convert_from_path(
                    file,
                    dpi=800, #the detail level that pdf's are processed at. 800 is fine for most small text while not being too ram intensive
                    first_page=page_number,
                    last_page=page_number
                )[0]

                text = pytesseract.image_to_string(page)
                file_contents.append(text)

                print(f"Processed page {page_number}/{total_pages} of '{file}'")

            return "\n".join(file_contents)
        elif format == "markdown": #un-implimented code to convert to markdown for easier llm usage
            markdown = pymupdf4llm.to_markdown(file)
            return markdown
    else:
        print(f"unsupported file type '{kind.extension}'!")
        return "--unsupported file--"