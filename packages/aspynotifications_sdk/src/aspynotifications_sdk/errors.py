class NotificationsClientError(Exception):
    pass


class NotFoundError(NotificationsClientError):
    pass


class UnauthorizedError(NotificationsClientError):
    pass


class BadRequestError(NotificationsClientError):
    pass


class ConflictError(NotificationsClientError):
    pass


class ServerError(NotificationsClientError):
    pass


class TimeoutError(NotificationsClientError):
    pass


class TransportError(NotificationsClientError):
    pass
