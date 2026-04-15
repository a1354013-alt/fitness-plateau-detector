from .analytics import router as analytics_router
from .health_records import router as health_records_router

__all__ = ["health_records_router", "analytics_router"]
