import base64
import base64
from bs4 import BeautifulSoup

class GmailParserService:

    @staticmethod
    def html_to_text(html):

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        return soup.get_text(
            separator=" ",
            strip=True
        )
    
    @staticmethod
    def decode_data(data):

        text = (
            base64.urlsafe_b64decode(data)
            .decode(
                "utf-8",
                errors="ignore"
            )
        )

        if "<html" in text.lower():

            return (
                GmailParserService
                .html_to_text(text)
            )

        return text
    
    @staticmethod
    def get_body(payload):

        # multipart emails

        if "parts" in payload:

            for part in payload["parts"]:

                mime_type = part.get(
                    "mimeType",
                    ""
                )

                data = (
                    part.get(
                        "body",
                        {}
                    )
                    .get("data")
                )

                if data and (
                    mime_type == "text/plain"
                    or mime_type == "text/html"
                ):
                    return (
                        GmailParserService
                        .decode_data(data)
                    )

                if "parts" in part:

                    nested = (
                        GmailParserService
                        .get_body(part)
                    )

                    if nested:
                        return nested

        # single-part emails

        data = (
            payload.get(
                "body",
                {}
            )
            .get("data")
        )

        if data:

            return (
                GmailParserService
                .decode_data(data)
            )

        return ""