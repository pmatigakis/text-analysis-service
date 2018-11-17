from tas.exceptions import TASError


class HTMLContentProcessorError(TASError):
    """Exception that is raised when the page content could not be processed"""
    pass


class UnsupportedContentType(TASError):
    """Exception that is raised when the content type is not supported"""

    def __init__(self, content_type=None):
        """Create a new UnsupportedContentType exception

        :param str|None content_type: the content type
        """
        super(UnsupportedContentType, self).__init__(content_type)

        self.content_type = content_type
