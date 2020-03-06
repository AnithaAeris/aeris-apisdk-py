class ApiException(Exception):
    """
    Represents an exception with an Aeris API, such as a device not being found or invalid authentication credentials.
    Does not represent transport-layer problems, such as not being able to reach the Aeris APIs.
    The 'response' attribute will have, at least, the following attributes:
    * status_code, to represent the HTTP status code from the response
    * headers, to represent the HTTP headers sent in the response
    * text, to represent the body of the HTTP response
    """
    def __init__(self, message, response, *args, **kwargs):
        super(Exception, self).__init__(message)
        self.message = message
        self.response = response
