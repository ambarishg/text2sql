from pypdf import PdfReader, PdfWriter
import os
from azure_blob.azure_blob_helper import AzureBlobHelper
import io
import html

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeResult

from config import *

import re

MAX_SECTION_LENGTH = 1000
SENTENCE_SEARCH_LIMIT = 100
SECTION_OVERLAP = 100

class PDFHelper:
    def __init__(self, pdf_path,azure_blob_helper,
                 category=None,
                 localpdfparser=True,
                 verbose=False):
        self.pdf_path = pdf_path
        self.azure_blob_helper = azure_blob_helper
        self.localpdfparser = localpdfparser
        self.verbose = verbose
        self.category = category
    
    def blob_name_from_file_page(self,filename, page = 0):
        if os.path.splitext(filename)[1].lower() == ".pdf":
            return os.path.splitext(os.path.basename(filename))[0] + f"-{page}" + ".pdf"
        else:
            return os.path.basename(filename)
    
    def write_pdf(self,verbose=False):
        reader = PdfReader(self.pdf_path)
        pages = reader.pages
        for i in range(len(pages)):
            blob_name = self.blob_name_from_file_page(self.pdf_path, i)
            if verbose: print(f"\tUploading blob for page {i} -> {blob_name}")
            f = io.BytesIO()
            writer = PdfWriter()
            writer.add_page(pages[i])
            writer.write(f)
            f.seek(0)
            self.azure_blob_helper.upload_blob(f, blob_name)

    def table_to_html(self,table):
        table_html = "<table>"
        rows = [sorted([cell for cell in table.cells if cell.row_index == i], key=lambda cell: cell.column_index) for i in range(table.row_count)]
        for row_cells in rows:
            table_html += "<tr>"
            for cell in row_cells:
                tag = "th" if (cell.kind == "columnHeader" or cell.kind == "rowHeader") else "td"
                cell_spans = ""
                if cell.column_span > 1: cell_spans += f" colSpan={cell.column_span}"
                if cell.row_span > 1: cell_spans += f" rowSpan={cell.row_span}"
                table_html += f"<{tag}{cell_spans}>{html.escape(cell.content)}</{tag}>"
            table_html +="</tr>"
        table_html += "</table>"
        return table_html

    def get_document_text(self,filename):
        offset = 0
        page_map = []
        if self.localpdfparser:
            reader = PdfReader(filename)
            pages = reader.pages
            for page_num, p in enumerate(pages):
                page_text = p.extract_text()
                page_map.append((page_num, offset, page_text))
                offset += len(page_text)
        else:
            if self.verbose: 
                print(f"Extracting text from '{filename}' using Azure Form Recognizer")
                print(f"Using Form Recognizer endpoint {DOC_INTELLIGENCE_ENDPOINT} and key {DOC_INTELLIGENCE_KEY}")
            formrecognizer_creds = AzureKeyCredential(DOC_INTELLIGENCE_KEY)
            form_recognizer_client = DocumentIntelligenceClient(endpoint=DOC_INTELLIGENCE_ENDPOINT,
                                                                 credential=formrecognizer_creds)
            with open(filename, "rb") as f:
                poller = form_recognizer_client.begin_analyze_document(
                    "prebuilt-layout",
                    analyze_request=f,
                    features=[DocumentAnalysisFeature.KEY_VALUE_PAIRS],
                    content_type="application/octet-stream",
                )
            form_recognizer_results: AnalyzeResult = poller.result()

            for page_num, page in enumerate(form_recognizer_results.pages):
                tables_on_page = [table for table in form_recognizer_results.tables if table.bounding_regions[0].page_number == page_num + 1]

                # mark all positions of the table spans in the page
                page_offset = page.spans[0].offset
                page_length = page.spans[0].length
                table_chars = [-1]*page_length
                for table_id, table in enumerate(tables_on_page):
                    for span in table.spans:
                        # replace all table spans with "table_id" in table_chars array
                        for i in range(span.length):
                            idx = span.offset - page_offset + i
                            if idx >=0 and idx < page_length:
                                table_chars[idx] = table_id

                # build page text by replacing charcters in table spans with table html
                page_text = ""
                added_tables = set()
                for idx, table_id in enumerate(table_chars):
                    if table_id == -1:
                        page_text += form_recognizer_results.content[page_offset + idx]
                    elif not table_id in added_tables:
                        page_text += self.table_to_html(tables_on_page[table_id])
                        added_tables.add(table_id)

                page_text += " "
                page_map.append((page_num, offset, page_text))
                offset += len(page_text)

        return page_map

    def split_text(self,page_map):
        SENTENCE_ENDINGS = [".", "!", "?"]
        WORDS_BREAKS = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]
        if self.verbose: print(f"Splitting '{self.pdf_path}' into sections")

        def find_page(offset):
            l = len(page_map)
            for i in range(l - 1):
                if offset >= page_map[i][1] and offset < page_map[i + 1][1]:
                    return i
            return l - 1

        all_text = "".join(p[2] for p in page_map)
        length = len(all_text)
        start = 0
        end = length
        while start + SECTION_OVERLAP < length:
            last_word = -1
            end = start + MAX_SECTION_LENGTH

            if end > length:
                end = length
            else:
                # Try to find the end of the sentence
                while end < length and (end - start - MAX_SECTION_LENGTH) < SENTENCE_SEARCH_LIMIT and all_text[end] not in SENTENCE_ENDINGS:
                    if all_text[end] in WORDS_BREAKS:
                        last_word = end
                    end += 1
                if end < length and all_text[end] not in SENTENCE_ENDINGS and last_word > 0:
                    end = last_word # Fall back to at least keeping a whole word
            if end < length:
                end += 1

            # Try to find the start of the sentence or at least a whole word boundary
            last_word = -1
            while start > 0 and start > end - MAX_SECTION_LENGTH - 2 * SENTENCE_SEARCH_LIMIT and all_text[start] not in SENTENCE_ENDINGS:
                if all_text[start] in WORDS_BREAKS:
                    last_word = start
                start -= 1
            if all_text[start] not in SENTENCE_ENDINGS and last_word > 0:
                start = last_word
            if start > 0:
                start += 1

            section_text = all_text[start:end]
            yield (section_text, find_page(start))

            last_table_start = section_text.rfind("<table")
            if (last_table_start > 2 * SENTENCE_SEARCH_LIMIT and last_table_start > section_text.rfind("</table")):
                # If the section ends with an unclosed table, we need to start the next section with the table.
                # If table starts inside SENTENCE_SEARCH_LIMIT, we ignore it, as that will cause an infinite loop for tables longer than MAX_SECTION_LENGTH
                # If last table starts inside SECTION_OVERLAP, keep overlapping
                if self.verbose: print(f"Section ends with unclosed table, starting next section with the table at page {find_page(start)} offset {start} table start {last_table_start}")
                start = min(end - SECTION_OVERLAP, start + last_table_start)
            else:
                start = end - SECTION_OVERLAP
            
        if start + SECTION_OVERLAP < end:
            yield (all_text[start:end], find_page(start))

    def create_sections(self,filename, page_map):
        for i, (section, pagenum) in enumerate(self.split_text(page_map)):
            yield {
                "id": re.sub("[^0-9a-zA-Z_-]","_",f"{filename}-{i}"),
                "content": section,
                "category": self.category,
                "sourcepage": self.blob_name_from_file_page(filename, pagenum),
                "sourcefile": os.path.basename(self.pdf_path)
            }

