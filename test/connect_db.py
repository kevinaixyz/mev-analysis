from mev_analysis.db import get_inspect_session, get_inspect_database_uri
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_db_connection():
    uri = get_inspect_database_uri()
    engine = create_engine(uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    print(session)


def test_get_inspect_session():
    session = get_inspect_session()
    print(session)

# test_get_inspect_session()
test_get_inspect_session()