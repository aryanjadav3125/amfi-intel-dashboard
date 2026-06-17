from typing import List
from scraper.models import SchemeRecord
from scraper.nav_parser import NavParser

class MetadataParser:
    """
    Supplements scheme metadata parsing.
    Delegates to NavParser since the AMFI file contains both metadata and NAV data.
    """
    def __init__(self):
        self.parser = NavParser()

    def parse_metadata(self, raw_text: str) -> List[SchemeRecord]:
        schemes, _ = self.parser.parse_raw_text(raw_text)
        return schemes
