from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BrandBase(BaseModel):
    name: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    aliases: List[str] = []
    keywords: List[str] = []
    product_names: List[str] = []
    service_names: List[str] = []
    official_developer_names: List[str] = []
    official_email_domains: List[str] = []


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    aliases: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    product_names: Optional[List[str]] = None
    service_names: Optional[List[str]] = None
    official_developer_names: Optional[List[str]] = None
    official_email_domains: Optional[List[str]] = None


class BrandOut(BrandBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OfficialMobileAppBase(BaseModel):
    name: str
    package_id: Optional[str] = None
    bundle_id: Optional[str] = None
    store_url: Optional[str] = None
    developer_name: Optional[str] = None
    developer_website: Optional[str] = None
    developer_email: Optional[str] = None
    platform: Optional[str] = "unknown"
    store: Optional[str] = "DEMO"
    icon_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class OfficialMobileAppCreate(OfficialMobileAppBase):
    brand_id: int


class OfficialMobileAppUpdate(BaseModel):
    name: Optional[str] = None
    package_id: Optional[str] = None
    bundle_id: Optional[str] = None
    store_url: Optional[str] = None
    developer_name: Optional[str] = None
    developer_website: Optional[str] = None
    developer_email: Optional[str] = None
    platform: Optional[str] = None
    store: Optional[str] = None
    icon_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class OfficialMobileAppOut(OfficialMobileAppBase):
    id: int
    brand_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppCandidateBase(BaseModel):
    app_name: str
    normalized_app_name: Optional[str] = None
    store: str = "DEMO"
    platform: str = "unknown"
    app_url: Optional[str] = None
    package_id: Optional[str] = None
    bundle_id: Optional[str] = None
    developer_name: Optional[str] = None
    developer_website: Optional[str] = None
    developer_email: Optional[str] = None
    app_icon_url: Optional[str] = None
    app_description: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    download_count: Optional[int] = None
    external_links: List[str] = []
    collection_source: str = "DEMO"


class AppCandidateCreate(AppCandidateBase):
    brand_id: int
    scan_job_id: Optional[int] = None


class AppCandidateOut(AppCandidateBase):
    id: int
    brand_id: int
    scan_job_id: Optional[int] = None
    collected_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppScanJobBase(BaseModel):
    brand_id: int
    source_type: str = "DEMO"


class AppScanJobCreate(AppScanJobBase):
    pass


class AppScanJobOut(AppScanJobBase):
    id: int
    status: str
    total_candidates: int
    official_count: int
    suspicious_count: int
    likely_impersonation_count: int
    high_risk_count: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AppSignalOut(BaseModel):
    signal_name: str
    signal_value: Optional[str] = None
    weight: int
    contributed_score: int


class AppDetectionResultBase(BaseModel):
    classification: str
    threat: bool
    risk_score: int
    risk_level: str
    confidence: float

    name_similarity: Optional[int] = None
    logo_similarity: Optional[int] = None
    description_similarity: Optional[int] = None
    branding_similarity: Optional[int] = None

    developer_match: str
    developer_domain_match: Optional[bool] = None
    package_match: Optional[bool] = None
    bundle_match: Optional[bool] = None

    lookalike_detected: bool
    lookalike_pattern: Optional[str] = None

    official_match_id: Optional[int] = None
    official_match_type: Optional[str] = None

    reasons: List[str] = []
    signals: Dict[str, Any] = {}
    source_data: Dict[str, Any] = {}

    status: str = "NEW"


class AppDetectionResultCreate(AppDetectionResultBase):
    brand_id: int
    candidate_id: int
    scan_job_id: Optional[int] = None


class AppDetectionResultOut(AppDetectionResultBase):
    id: int
    brand_id: int
    candidate_id: int
    scan_job_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    candidate: Optional[AppCandidateOut] = None
    official_match: Optional[OfficialMobileAppOut] = None

    model_config = ConfigDict(from_attributes=True)


class AppThreatOut(BaseModel):
    id: str
    brand_id: str
    source_type: str
    store: str
    candidate: Dict[str, Any]
    signals: Dict[str, Any]
    lookalike: Dict[str, Any]
    official_match: Dict[str, Any]
    risk_score: int
    risk_level: str
    confidence: float
    classification: str
    reasons: List[str]
    source: Dict[str, Any]
    status: str

    model_config = ConfigDict(from_attributes=True)


class AppScanStartRequest(BaseModel):
    source_type: str = "DEMO"


class AppScanStartResponse(BaseModel):
    scan_job_id: int
    status: str
    message: str


class AppThreatsQueryParams(BaseModel):
    search: Optional[str] = None
    store: Optional[str] = None
    risk_level: Optional[str] = None
    classification: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0


class AppScanStatusResponse(BaseModel):
    scan_job_id: int
    status: str
    total_candidates: int
    official_count: int
    suspicious_count: int
    likely_impersonation_count: int
    high_risk_count: int
    error_message: Optional[str] = None