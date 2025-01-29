class ConfigError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return ""

    def __str__(self):
        return self._format_message()


class BlaiseError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return ""

    def __str__(self):
        return self._format_message()


class IngestError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return ""

    def __str__(self):
        return self._format_message()
