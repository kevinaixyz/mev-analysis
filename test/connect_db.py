from mev_analysis.db import get_inspect_session, get_inspect_database_uri, get_trace_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_TRACE_SQL = """
"""


def test_get_inspect_session():
    session = get_inspect_session()
    print(session)


# test_get_inspect_session()
