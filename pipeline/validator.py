from datetime import date
from typing import Optional
from scraper.models import NavRecord, SchemeRecord
from pipeline.exceptions import PipelineValidationError

class PipelineValidator:
    """
    Performs field validations and consistency checks on ingested mutual fund data.
    """
    @staticmethod
    def validate_nav_record(record: NavRecord) -> bool:
        """
        Validates NAV record constraints.
        Returns True if valid, raises PipelineValidationError if invalid.
        """
        if record.scheme_code <= 0:
            raise PipelineValidationError(
                f"Validation failed: Invalid scheme code '{record.scheme_code}'"
            )
            
        if record.nav_value is None or record.nav_value <= 0:
            raise PipelineValidationError(
                f"Validation failed: Scheme {record.scheme_code} has invalid NAV value '{record.nav_value}'"
            )
            
        if record.nav_date > date.today():
            raise PipelineValidationError(
                f"Validation failed: NAV date {record.nav_date} is in the future"
            )
            
        return True

    @staticmethod
    def validate_scheme_record(record: SchemeRecord) -> bool:
        """
        Validates scheme metadata constraints.
        """
        if record.scheme_code <= 0:
            raise PipelineValidationError(
                f"Validation failed: Invalid scheme code '{record.scheme_code}'"
            )
        if not record.scheme_name:
            raise PipelineValidationError(
                f"Validation failed: Scheme {record.scheme_code} has empty scheme name"
            )
        if not record.category:
            raise PipelineValidationError(
                f"Validation failed: Scheme {record.scheme_code} has empty category"
            )
        return True

    @staticmethod
    def validate_holding_record(record: dict) -> bool:
        """
        Validates holding data constraints.
        """
        if not record.get("company_name"):
            raise PipelineValidationError("Holding validation failed: empty company name")
        if not record.get("sector"):
            raise PipelineValidationError("Holding validation failed: empty sector")
        if record.get("allocation_percentage", -1) < 0 or record.get("allocation_percentage", 0) > 100:
            raise PipelineValidationError(f"Holding validation failed: invalid allocation percentage {record.get('allocation_percentage')}")
        return True
