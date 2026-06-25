import logging

from django.db import InterfaceError, OperationalError, close_old_connections, connections


logger = logging.getLogger(__name__)


class DatabaseConnectionRetryMiddleware:
    """Retry safe requests once when Postgres closes a stale connection."""

    recoverable_messages = (
        'terminating connection due to administrator command',
        'ssl connection has been closed unexpectedly',
        'server closed the connection unexpectedly',
        'connection already closed',
        'consuming input failed',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except (OperationalError, InterfaceError) as exc:
            if not self._can_retry(request, exc):
                raise

            logger.warning('Retrying request after database connection reset: %s', exc)
            connections.close_all()
            close_old_connections()
            request._db_connection_retry_attempted = True
            return self.get_response(request)

    def _can_retry(self, request, exc):
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            return False
        if getattr(request, '_db_connection_retry_attempted', False):
            return False
        message = str(exc).lower()
        return any(fragment in message for fragment in self.recoverable_messages)
