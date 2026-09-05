import logging
import os
import time
from threading import RLock
from logging.handlers import BaseRotatingHandler


class RequestFormatter(logging.Formatter):
    """
    Extends the default formatter to include HTTP method, path,
    and status code when the log record comes from a Django request.
    """

    def format(self, record):
        # Attach request info if available (set by django.request logger)
        request = getattr(record, 'request', None)
        if request:
            record.http_method = request.method
            record.http_path = request.get_full_path()
        else:
            record.http_method = '-'
            record.http_path = '-'

        record.status_code = getattr(record, 'status_code', '-')

        return super().format(record)


class AppFileHandler(BaseRotatingHandler):
    """
    Logs always write to a fixed `logs.log`.
    On rollover (size >= 50MB or date change), the active file is
    renamed to logs-YYYY-MM-DD-N.log and a fresh logs.log is opened.
    """

    def __init__(self, log_dir,
                 active_filename='logs.log',
                 rotated_pattern='logs-{date}-{seq}.log',
                 max_bytes=50 * 1024 * 1024,
                 encoding=None):

        self.log_dir = log_dir
        self.active_filename = active_filename
        self.rotated_pattern = rotated_pattern
        self.max_bytes = max_bytes
        self.lock = RLock()

        os.makedirs(self.log_dir, exist_ok=True)

        active_path = os.path.join(self.log_dir, self.active_filename)
        super().__init__(filename=active_path, mode='a', encoding=encoding)

        self._current_date = self._get_active_file_date()

    def _get_active_file_date(self):
        active_path = os.path.join(self.log_dir, self.active_filename)
        if os.path.exists(active_path) and os.path.getsize(active_path) > 0:
            mtime = os.path.getmtime(active_path)
            return time.strftime('%Y-%m-%d', time.localtime(mtime))
        return time.strftime('%Y-%m-%d')

    def _next_rotated_path(self, date_str):
        seq = 1
        while True:
            filename = self.rotated_pattern.format(date=date_str, seq=seq)
            filepath = os.path.join(self.log_dir, filename)
            if not os.path.exists(filepath):
                return filepath
            seq += 1

    def shouldRollover(self, record):
        with self.lock:
            today = time.strftime('%Y-%m-%d')
            if self._current_date != today:
                return True
            if self.max_bytes > 0 and self.stream:
                return self.stream.tell() >= self.max_bytes
            return False

    def doRollover(self):
        with self.lock:
            if self.stream:
                self.stream.flush()
                self.stream.close()
                self.stream = None

            active_path = os.path.join(self.log_dir, self.active_filename)

            if os.path.exists(active_path) and os.path.getsize(active_path) > 0:
                dest_path = self._next_rotated_path(self._current_date)
                os.rename(active_path, dest_path)

            self._current_date = time.strftime('%Y-%m-%d')
            self.stream = open(active_path, 'a', encoding=self.encoding)

    def emit(self, record):
        with self.lock:
            try:
                if self.shouldRollover(record):
                    self.doRollover()
                logging.FileHandler.emit(self, record)
            except Exception:
                self.handleError(record)


def get_logger(name):
    return logging.getLogger(name)


def configure_logging():
    from django.conf import settings

    if getattr(settings, 'LOGGING_CONFIGURED', False):
        return

    LOGS_DIR = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Use RequestFormatter so django.request logs show method + path + status
    formatter = RequestFormatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(http_method)s %(http_path)s %(status_code)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Fallback formatter for non-request loggers (no http fields)
    plain_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if getattr(
        settings, 'DEBUG', False) else logging.INFO)
    root_logger.handlers.clear()

    file_handler = AppFileHandler(
        log_dir=LOGS_DIR,
        active_filename='logs.log',
        rotated_pattern='logs-{date}-{seq}.log',
        max_bytes=50 * 1024 * 1024
    )
    file_handler.setLevel(logging.DEBUG if getattr(
        settings, 'DEBUG', False) else logging.INFO)
    # RequestFormatter handles both request and non-request records gracefully
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if getattr(settings, 'DEBUG', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    settings.LOGGING_CONFIGURED = True
