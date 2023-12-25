from typing import Optional

from mev_analysis.schemas.traces import Trace
from mev_analysis.schemas.utils import CamelModel
import json

class AvaxCallTrace(CamelModel):
    tx_hash: Optional[str]
    type: Optional[str]
    error: Optional[str] = None
