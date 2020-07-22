import json
import logging
import socket

from django.utils import timezone

from nayzi.custom_middleware import get_current_request_ip, get_correlation_id

logger = logging.getLogger('transaction')


class TransactionLogger:
    @staticmethod
    def debug(parameters):
        transaction = {
            'correlation_id': get_correlation_id(),
            'ip': get_current_request_ip(),
            'hostname': socket.gethostname(), 'time': str(timezone.now()), **parameters
        }
        logger.info(json.dumps(transaction))


transaction_logger = TransactionLogger()
