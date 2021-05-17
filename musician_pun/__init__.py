import logging
import sys

logger = logging.getLogger('musician_pun')

logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(
    '%(asctime)s|%(levelname)s|%(name)s|%(message)s'
))
logger.addHandler(handler)

from .bot import Bot, main
