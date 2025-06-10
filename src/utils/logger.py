import logging 
class FileFuncFormatter(logging.Formatter):
    def format(self, record):
        combined = f"{record.filename}::{record.funcName}()"
        record.filefunc = f"{combined:<37}"  # Left-align in 35-char field
        return super().format(record)
    
def init_logger():
    log_format = (
        '{asctime} | {levelname:<6} | {filefunc} | {message}'
    )

    # Use the custom formatter
    formatter = FileFuncFormatter(
        log_format,
        style='{',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler('bot.log', mode='a')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console)
