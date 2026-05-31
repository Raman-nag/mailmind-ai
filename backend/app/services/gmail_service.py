from googleapiclient.discovery import build


class GmailService:

    @staticmethod
    def create_service(credentials):

        return build(
            "gmail",
            "v1",
            credentials=credentials
        )

    @staticmethod
    def list_messages(
        service,
        max_results: int = 10
    ):

        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                maxResults=max_results
            )
            .execute()
        )

        return results.get(
            "messages",
            []
        )

    @staticmethod
    def get_message(
        service,
        message_id: str
    ):

        return (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id
            )
            .execute()
        )
    
    @staticmethod
    def extract_header(
        headers,
        name: str
    ):

        for header in headers:

            if header["name"] == name:
                return header["value"]

        return ""