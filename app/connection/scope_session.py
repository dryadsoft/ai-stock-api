from contextlib import contextmanager
from sqlalchemy.orm import scoped_session
from ..connection.connection import SessionLocal

Session = scoped_session(SessionLocal)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()
