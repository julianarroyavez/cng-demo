from playhouse.postgres_ext import PostgresqlExtDatabase

from app import config
from app import log

LOG = log.get_logger()

# "pool_recycle": 3600,
# "pool_size": 10,
# "pool_timeout": 30,
# "max_overflow": 30,
# "echo": config.DB_ECHO,
# "execution_options": {"autocommit": config.DB_AUTOCOMMIT},

db_config = config.POSTGRES
db_session = PostgresqlExtDatabase(
    db_config['database'],
    user=db_config['user'],
    password=db_config['password'],
    host=db_config['host'],
    port=db_config['port'],
    options=db_config['options'],
    register_hstore=True
)


def init_session():
    pass # empty function

