import logging

import coloredlogs

logger = logging.getLogger('musician_pun')
coloredlogs.DEFAULT_FIELD_STYLES['name'] = {'color': 'white', 'faint': True}
coloredlogs.install(
    level='DEBUG', logger=logger,
    fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
)

from .bot import Bot, main
