from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.logger import Logger
from .. import config_yaml

logger = Logger().get_logger(__name__)

is_prod_server: bool = config_yaml.get_propertity("is_prod_server")

if is_prod_server:
    server = config_yaml.get_propertity("server_prod")
else:
    server = config_yaml.get_propertity("server_dev")

database = server["database"]
is_echo = False if is_prod_server else True

logger.info(f"is_echo={is_echo}, database={database}")

engine = create_engine(database, echo=is_echo)  # echo=True 쿼리문 콘솔로그활성화

# Session = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
