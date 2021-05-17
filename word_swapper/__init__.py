import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import coloredlogs

logger = logging.getLogger(__name__)
log_format = '%(asctime)s %(name)s %(levelname)s %(message)s'

coloredlogs.DEFAULT_FIELD_STYLES['name'] = {'color': 'white', 'faint': True}
coloredlogs.install(level='DEBUG', logger=logger, fmt=log_format)

handler = TimedRotatingFileHandler(
    filename=Path(__file__, '../logs/musician_pun.log'),
    when='midnight',
    interval=1,
    backupCount=7,
)
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
logger.addHandler(handler)

from .bot import Bot, main
