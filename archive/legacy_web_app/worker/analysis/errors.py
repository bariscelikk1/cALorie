class AnalysisError(Exception):
    """An expected, user-safe analysis failure."""


class InvalidVideoError(AnalysisError):
    pass


class PoseNotDetectedError(AnalysisError):
    pass

