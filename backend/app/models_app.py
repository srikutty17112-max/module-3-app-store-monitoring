from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.types import TypeDecorator
import json
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class JSONList(TypeDecorator):
    """Pluggable JSON type that stores as text and returns as list."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return '[]'
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return json.loads(value)


class AppStoreSource(str, enum.Enum):
    DEMO = "DEMO"
    GOOGLE_PLAY = "GOOGLE_PLAY"
    APPLE_APP_STORE = "APPLE_APP_STORE"
    IMPORTED = "IMPORTED"
    MOCK = "MOCK"


class AppPlatform(str, enum.Enum):
    ANDROID = "android"
    IOS = "ios"
    UNKNOWN = "unknown"


class AppClassification(str, enum.Enum):
    OFFICIAL = "OFFICIAL"
    LIKELY_LEGITIMATE = "LIKELY_LEGITIMATE"
    SUSPICIOUS = "SUSPICIOUS"
    LIKELY_IMPERSONATION = "LIKELY_IMPERSONATION"
    HIGH_RISK_IMPERSONATION = "HIGH_RISK_IMPERSONATION"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatStatus(str, enum.Enum):
    NEW = "NEW"
    REVIEWING = "REVIEWING"
    CONFIRMED = "CONFIRMED"
    DISMISSED = "DISMISSED"


class DeveloperMatchType(str, enum.Enum):
    EXACT_MATCH = "EXACT_MATCH"
    STRONG_MATCH = "STRONG_MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


class LookalikePattern(str, enum.Enum):
    CHARACTER_SWAP = "CHARACTER_SWAP"
    ADDED_WORD = "ADDED_WORD"
    REMOVED_CHARACTER = "REMOVED_CHARACTER"
    EXTRA_CHARACTER = "EXTRA_CHARACTER"
    SPACING_CHANGE = "SPACING_CHANGE"
    PUNCTUATION_CHANGE = "PUNCTUATION_CHANGE"
    CHARACTER_SUBSTITUTION = "CHARACTER_SUBSTITUTION"
    CASE_VARIATION = "CASE_VARIATION"


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    website = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    aliases = Column(JSONList, default=[])
    keywords = Column(JSONList, default=[])
    product_names = Column(JSONList, default=[])
    service_names = Column(JSONList, default=[])
    official_developer_names = Column(JSONList, default=[])
    official_email_domains = Column(JSONList, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    official_apps = relationship("OfficialMobileApp", back_populates="brand", cascade="all, delete-orphan")
    app_candidates = relationship("AppCandidate", back_populates="brand", cascade="all, delete-orphan")
    detection_results = relationship("AppDetectionResult", back_populates="brand", cascade="all, delete-orphan")
    scan_jobs = relationship("AppScanJob", back_populates="brand", cascade="all, delete-orphan")


class OfficialMobileApp(Base):
    __tablename__ = "official_mobile_apps"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    package_id = Column(String(255), nullable=True, index=True)
    bundle_id = Column(String(255), nullable=True, index=True)
    store_url = Column(String(500), nullable=True)
    developer_name = Column(String(255), nullable=True)
    developer_website = Column(String(500), nullable=True)
    developer_email = Column(String(255), nullable=True)
    platform = Column(SQLEnum(AppPlatform), default=AppPlatform.UNKNOWN)
    store = Column(SQLEnum(AppStoreSource), default=AppStoreSource.DEMO)
    icon_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brand = relationship("Brand", back_populates="official_apps")


class AppCandidate(Base):
    __tablename__ = "app_candidates"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    scan_job_id = Column(Integer, ForeignKey("app_scan_jobs.id"), nullable=True, index=True)

    app_name = Column(String(255), nullable=False)
    normalized_app_name = Column(String(255), nullable=True)
    store = Column(SQLEnum(AppStoreSource), default=AppStoreSource.DEMO)
    platform = Column(SQLEnum(AppPlatform), default=AppPlatform.UNKNOWN)
    app_url = Column(String(500), nullable=True)
    package_id = Column(String(255), nullable=True, index=True)
    bundle_id = Column(String(255), nullable=True, index=True)
    developer_name = Column(String(255), nullable=True)
    developer_website = Column(String(500), nullable=True)
    developer_email = Column(String(255), nullable=True)
    app_icon_url = Column(String(500), nullable=True)
    app_description = Column(Text, nullable=True)
    short_description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    version = Column(String(50), nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    download_count = Column(Integer, nullable=True)
    external_links = Column(Text, default="[]")
    collection_source = Column(SQLEnum(AppStoreSource), default=AppStoreSource.DEMO)
    collected_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brand = relationship("Brand", back_populates="app_candidates")
    scan_job = relationship("AppScanJob", back_populates="candidates")
    detection_result = relationship("AppDetectionResult", back_populates="candidate", uselist=False, cascade="all, delete-orphan")


class AppScanJob(Base):
    __tablename__ = "app_scan_jobs"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    source_type = Column(SQLEnum(AppStoreSource), default=AppStoreSource.DEMO)
    status = Column(String(32), default="PENDING")
    total_candidates = Column(Integer, default=0)
    official_count = Column(Integer, default=0)
    suspicious_count = Column(Integer, default=0)
    likely_impersonation_count = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    brand = relationship("Brand", back_populates="scan_jobs")
    candidates = relationship("AppCandidate", back_populates="scan_job", cascade="all, delete-orphan")


class AppDetectionResult(Base):
    __tablename__ = "app_detection_results"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("app_candidates.id"), nullable=False, unique=True, index=True)
    scan_job_id = Column(Integer, ForeignKey("app_scan_jobs.id"), nullable=True, index=True)

    classification = Column(SQLEnum(AppClassification), default=AppClassification.SUSPICIOUS)
    threat = Column(Boolean, default=True)
    risk_score = Column(Integer, default=0)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW)
    confidence = Column(Float, default=0.0)

    name_similarity = Column(Integer, nullable=True)
    logo_similarity = Column(Integer, nullable=True)
    description_similarity = Column(Integer, nullable=True)
    branding_similarity = Column(Integer, nullable=True)

    developer_match = Column(SQLEnum(DeveloperMatchType), default=DeveloperMatchType.UNKNOWN)
    developer_domain_match = Column(Boolean, nullable=True)
    package_match = Column(Boolean, nullable=True)
    bundle_match = Column(Boolean, nullable=True)

    lookalike_detected = Column(Boolean, default=False)
    lookalike_pattern = Column(SQLEnum(LookalikePattern), nullable=True)

    official_match_id = Column(Integer, ForeignKey("official_mobile_apps.id"), nullable=True)
    official_match_type = Column(String(64), nullable=True)

    reasons = Column(Text, default="[]")
    signals = Column(Text, default="{}")
    source_data = Column(Text, default="{}")

    status = Column(SQLEnum(ThreatStatus), default=ThreatStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brand = relationship("Brand", back_populates="detection_results")
    candidate = relationship("AppCandidate", back_populates="detection_result")
    scan_job = relationship("AppScanJob")
    official_match = relationship("OfficialMobileApp")


class AppSignal(Base):
    __tablename__ = "app_signals"

    id = Column(Integer, primary_key=True, index=True)
    detection_result_id = Column(Integer, ForeignKey("app_detection_results.id"), nullable=False, index=True)
    signal_name = Column(String(64), nullable=False)
    signal_value = Column(Text, nullable=True)
    weight = Column(Integer, default=0)
    contributed_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)