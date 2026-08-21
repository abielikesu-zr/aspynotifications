class EventsClientError(Exception):
    pass


class NotFoundError(EventsClientError):
    pass


class UnauthorizedError(EventsClientError):
    pass


class BadRequestError(EventsClientError):
    pass


class ConflictError(EventsClientError):
    pass


class ServerError(EventsClientError):
    pass


class TimeoutError(EventsClientError):
    pass


class TransportError(EventsClientError):
    pass
