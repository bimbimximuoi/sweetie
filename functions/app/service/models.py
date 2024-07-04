import base64
from io import BytesIO

class Metadata:
    def __init__(self, title, authors, subject, keywords):
        self.title = title
        self.authors = authors
        self.subject = subject
        self.keywords = keywords

class TextData:
    def __init__(self, texts, cover_image, metadata):
        self.texts = texts
        self.cover_image = cover_image
        self.metadata = metadata

    @staticmethod
    def from_session(session_data):
        return TextData(
            texts=session_data.get('texts', {}),
            cover_image=session_data.get('cover_image', None),
            metadata=Metadata(
                title=session_data.get('metadata', {}).get('title', 'Unknown Title'),
                authors=session_data.get('metadata', {}).get('authors', []),
                subject=session_data.get('metadata', {}).get('subject', 'Unknown Subject'),
                keywords=session_data.get('metadata', {}).get('keywords', 'Unknown Keywords')
            )
        )

def to_base64(image):
    image.seek(0)
    return base64.b64encode(image.read()).decode('utf-8')
