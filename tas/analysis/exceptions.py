from tas.exceptions import TASError


class HTMLContentProcessorError(TASError):
    """Exception that is raised when the page content could not be processed"""
    pass


class InvalidHTMLContent(HTMLContentProcessorError):
    """Exception that is raised in the html content is invalid"""
    def __init__(self, errors=None):
        super(InvalidHTMLContent, self).__init__(errors)

        self.errors = errors


class HtmlContentProcessingError(HTMLContentProcessorError):
    """Exception that is raised when we fail to analyse the html contents"""
    pass
