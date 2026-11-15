import pytest

from warren_botfett.core.models import Instrument, InstrumentKind


@pytest.fixture
def yes_token() -> Instrument:
    return Instrument(venue="polymarket", symbol="123", kind=InstrumentKind.BINARY_OUTCOME)
