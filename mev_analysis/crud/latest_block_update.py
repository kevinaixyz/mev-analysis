from typing import Optional
from sqlalchemy import text

def find_latest_block_update(db_session) -> Optional[int]:
    result = db_session.execute(text(
        "SELECT block_number FROM latest_block_update LIMIT 1")
    ).one_or_none()
    if result is None:
        return None
    else:
        return int(result[0])


def update_latest_block(db_session, block_number) -> None:
    db_session.execute(text(
        """
            UPDATE latest_block_update
                SET block_number = :block_number, updated_at = current_timestamp;
            INSERT INTO latest_block_update
                (block_number, updated_at)
            SELECT :block_number, current_timestamp
                WHERE NOT EXISTS (SELECT 1 FROM latest_block_update);
            """),
        params={"block_number": block_number},
    )
