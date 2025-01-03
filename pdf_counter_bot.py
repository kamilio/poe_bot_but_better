from typing import AsyncIterable

import fastapi_poe as fp
import requests
from PyPDF2 import PdfReader


class FileDownloadError(Exception):
    pass


def _fetch_pdf_and_count_num_pages(url: str) -> int:
    response = requests.get(url)
    if response.status_code != 200:
        raise FileDownloadError()
    with open("temp_pdf_file.pdf", "wb") as f:
        f.write(response.content)
    reader = PdfReader("temp_pdf_file.pdf")
    return len(reader.pages)


class PDFSizeBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        yield fp.PartialResponse(
            text="Iterating over the pdfs uploaded in this conversation ..."
        )
        for message in reversed(request.query):
            for attachment in message.attachments:
                if attachment.content_type == "application/pdf":
                    try:
                        num_pages = _fetch_pdf_and_count_num_pages(attachment.url)
                        yield fp.PartialResponse(
                            text=f"{attachment.name} has {num_pages} pages.\n"
                        )
                    except FileDownloadError:
                        yield fp.PartialResponse(
                            text="Failed to retrieve the document."
                        )

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(allow_attachments=True)