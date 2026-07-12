"""Just enough of google.genai.types for gemini.py's imports and calls."""


class Part:
    def __init__(self, data=None, mime_type=None):
        self.data = data
        self.mime_type = mime_type

    @classmethod
    def from_bytes(cls, data=None, mime_type=None):
        return cls(data=data, mime_type=mime_type)


class ImageConfig:
    def __init__(self, aspect_ratio=None):
        self.aspect_ratio = aspect_ratio


class GenerateContentConfig:
    def __init__(self, response_modalities=None, image_config=None):
        self.response_modalities = response_modalities
        self.image_config = image_config
