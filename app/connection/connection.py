from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .. import config_yaml

database: str = config_yaml.get_propertity("database_dev")
is_dev: bool = config_yaml.get_propertity("envir") == "dev"

if is_dev == False:
    database = config_yaml.get_propertity("database_prod")


engine = create_engine(database, echo=is_dev)  # echo=True 쿼리문 콘솔로그활성화

# Session = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
