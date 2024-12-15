from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .. import config_yaml

is_prod_server: bool = config_yaml.get_propertity("is_prod_server")

if is_prod_server:
    server = config_yaml.get_propertity("server_prod")
else:
    server = config_yaml.get_propertity("server_dev")

database = server["database"]


engine = create_engine(
    database, echo=False if is_prod_server else True
)  # echo=True 쿼리문 콘솔로그활성화

# Session = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
