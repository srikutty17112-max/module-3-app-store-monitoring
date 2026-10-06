from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.schemas_app import AppCandidateCreate
import json


@dataclass
class RawAppData:
    app_name: str
    store: str
    platform: str
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
    external_links: List[str] = None
    raw_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.external_links is None:
            self.external_links = []
        if self.raw_data is None:
            self.raw_data = {}


class AppStoreSourceAdapter(ABC):
    SOURCE_TYPE: str = "BASE"
    PLATFORM: str = "unknown"

    @abstractmethod
    def collect_candidates(self, brand_name: str, keywords: List[str], official_apps: List[Dict]) -> List[RawAppData]:
        pass

    def normalize_candidate(self, raw: RawAppData, brand_id: int, scan_job_id: int) -> AppCandidateCreate:
        normalized_name = self._normalize_app_name(raw.app_name)
        return AppCandidateCreate(
            brand_id=brand_id,
            scan_job_id=scan_job_id,
            app_name=raw.app_name,
            normalized_app_name=normalized_name,
            store=self.SOURCE_TYPE,
            platform=self.PLATFORM,
            app_url=raw.app_url,
            package_id=raw.package_id,
            bundle_id=raw.bundle_id,
            developer_name=raw.developer_name,
            developer_website=raw.developer_website,
            developer_email=raw.developer_email,
            app_icon_url=raw.app_icon_url,
            app_description=raw.app_description,
            short_description=raw.short_description,
            category=raw.category,
            version=raw.version,
            rating=raw.rating,
            review_count=raw.review_count,
            download_count=raw.download_count,
            external_links=raw.external_links or [],
            collection_source=self.SOURCE_TYPE,
        )

    def _normalize_app_name(self, name: str) -> str:
        import re
        name = name.lower().strip()
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        return name


class DemoAppStoreAdapter(AppStoreSourceAdapter):
    SOURCE_TYPE = "DEMO"
    PLATFORM = "android"

    def __init__(self):
        self.demo_data = self._load_demo_data()

    def _load_demo_data(self) -> List[RawAppData]:
        return [
            RawAppData(
                app_name="KampusVC",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.kampusvc.app",
                package_id="com.kampusvc.app",
                bundle_id=None,
                developer_name="KampusVC Inc.",
                developer_website="https://kampusvc.com",
                developer_email="support@kampusvc.com",
                app_icon_url="https://example.com/icons/kampusvc.png",
                app_description="Official KampusVC app for student campus management, course registration, and academic resources.",
                short_description="Campus management for students",
                category="Education",
                version="3.2.1",
                rating=4.5,
                review_count=12500,
                download_count=500000,
                external_links=["https://kampusvc.com", "https://twitter.com/kampusvc"],
                raw_data={"source": "DEMO", "is_official": True}
            ),
            RawAppData(
                app_name="KampussVC",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.kampussvc.fake",
                package_id="com.kampussvc.fake",
                bundle_id=None,
                developer_name="KampussVC Dev Team",
                developer_website="https://kampussvc-support.com",
                developer_email="support@kampussvc-support.com",
                app_icon_url="https://example.com/icons/kampussvc.png",
                app_description="Official KampusVC app for student campus management, course registration, and academic resources.",
                short_description="Campus management for students",
                category="Education",
                version="2.1.0",
                rating=3.8,
                review_count=1200,
                download_count=50000,
                external_links=["https://kampussvc-support.com"],
                raw_data={"source": "DEMO", "is_official": False, "lookalike": True}
            ),
            RawAppData(
                app_name="KampusVC Support",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.kampusvc.support",
                package_id="com.kampusvc.support",
                bundle_id=None,
                developer_name="Student Helper Apps",
                developer_website="https://studenthelperapps.com",
                developer_email="help@studenthelperapps.com",
                app_icon_url="https://example.com/icons/kampusvc_support.png",
                app_description="Helper app for KampusVC students with campus maps, schedules, and support contacts.",
                short_description="Support helper for KampusVC",
                category="Education",
                version="1.0.5",
                rating=4.1,
                review_count=3400,
                download_count=100000,
                external_links=["https://studenthelperapps.com"],
                raw_data={"source": "DEMO", "is_official": False, "lookalike": True, "pattern": "ADDED_WORD"}
            ),
            RawAppData(
                app_name="KampusVC Official",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.fake.kampusvc.official",
                package_id="com.fake.kampusvc.official",
                bundle_id=None,
                developer_name="Official Apps Studio",
                developer_website="https://officialappsstudio.com",
                developer_email="contact@officialappsstudio.com",
                app_icon_url="https://example.com/icons/kampusvc_official.png",
                app_description="The official KampusVC application for managing your campus life, courses, and grades.",
                short_description="Official campus management",
                category="Education",
                version="1.2.0",
                rating=4.0,
                review_count=890,
                download_count=25000,
                external_links=["https://officialappsstudio.com"],
                raw_data={"source": "DEMO", "is_official": False, "lookalike": True, "pattern": "ADDED_WORD"}
            ),
            RawAppData(
                app_name="Kampus VC Student",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.kampusvc.student",
                package_id="com.kampusvc.student",
                bundle_id=None,
                developer_name="KampusVC Inc.",
                developer_website="https://kampusvc.com",
                developer_email="support@kampusvc.com",
                app_icon_url="https://example.com/icons/kampusvc_student.png",
                app_description="Student portal for KampusVC - access your courses, grades, and campus information.",
                short_description="Student portal",
                category="Education",
                version="2.0.0",
                rating=4.3,
                review_count=5600,
                download_count=200000,
                external_links=["https://kampusvc.com"],
                raw_data={"source": "DEMO", "is_official": True, "variant": "student"}
            ),
            RawAppData(
                app_name="Unrelated Campus App",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.unrelated.campus",
                package_id="com.unrelated.campus",
                bundle_id=None,
                developer_name="Campus Solutions Ltd",
                developer_website="https://campussolutions.example.com",
                developer_email="info@campussolutions.example.com",
                app_icon_url="https://example.com/icons/unrelated_campus.png",
                app_description="General campus management application for universities and colleges worldwide.",
                short_description="University campus management",
                category="Education",
                version="4.1.2",
                rating=4.2,
                review_count=8900,
                download_count=300000,
                external_links=["https://campussolutions.example.com"],
                raw_data={"source": "DEMO", "is_official": False, "unrelated": True}
            ),
            RawAppData(
                app_name="Generic VC Application",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.generic.vcapp",
                package_id="com.generic.vcapp",
                bundle_id=None,
                developer_name="Generic Apps Co",
                developer_website="https://genericapps.example.com",
                developer_email="support@genericapps.example.com",
                app_icon_url="https://example.com/icons/generic_vc.png",
                app_description="Venture capital tracking and portfolio management application.",
                short_description="VC portfolio tracker",
                category="Finance",
                version="1.5.0",
                rating=3.9,
                review_count=1200,
                download_count=15000,
                external_links=["https://genericapps.example.com"],
                raw_data={"source": "DEMO", "is_official": False, "unrelated": True}
            ),
            RawAppData(
                app_name="Kampus",
                store="DEMO",
                platform="ios",
                app_url="https://apps.apple.com/app/id123456789",
                package_id=None,
                bundle_id="com.kampusvc.ios",
                developer_name="KampusVC Inc.",
                developer_website="https://kampusvc.com",
                developer_email="support@kampusvc.com",
                app_icon_url="https://example.com/icons/kampusvc_ios.png",
                app_description="Official KampusVC iOS app for campus management.",
                short_description="iOS campus management",
                category="Education",
                version="3.2.0",
                rating=4.6,
                review_count=8900,
                download_count=300000,
                external_links=["https://kampusvc.com"],
                raw_data={"source": "DEMO", "is_official": True}
            ),
            RawAppData(
                app_name="KampusVC Pro",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.kampusvc.pro.fake",
                package_id="com.kampusvc.pro.fake",
                bundle_id=None,
                developer_name="Pro Apps Studio",
                developer_website="https://proappsstudio.example.com",
                developer_email="pro@proappsstudio.example.com",
                app_icon_url="https://example.com/icons/kampusvc_pro.png",
                app_description="Professional version of KampusVC with advanced features for campus administrators.",
                short_description="Pro campus admin",
                category="Education",
                version="1.0.0",
                rating=3.5,
                review_count=450,
                download_count=12000,
                external_links=["https://proappsstudio.example.com"],
                raw_data={"source": "DEMO", "is_official": False, "lookalike": True, "pattern": "ADDED_WORD"}
            ),
            RawAppData(
                app_name="KampusVC",
                store="DEMO",
                platform="android",
                app_url="https://play.google.com/store/apps/details?id=com.another.kampusvc",
                package_id="com.another.kampusvc",
                bundle_id=None,
                developer_name="Another Developer",
                developer_website="https://anotherdev.example.com",
                developer_email="info@anotherdev.example.com",
                app_icon_url="https://example.com/icons/another_kampusvc.png",
                app_description="Campus virtual classroom for online learning and student engagement.",
                short_description="Virtual classroom",
                category="Education",
                version="2.3.0",
                rating=4.0,
                review_count=2100,
                download_count=75000,
                external_links=["https://anotherdev.example.com"],
                raw_data={"source": "DEMO", "is_official": False, "incomplete": True}
            ),
        ]

    def collect_candidates(self, brand_name: str, keywords: List[str], official_apps: List[Dict]) -> List[RawAppData]:
        return self.demo_data.copy()


class GooglePlayStoreAdapter(AppStoreSourceAdapter):
    SOURCE_TYPE = "GOOGLE_PLAY"
    PLATFORM = "android"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.enabled = bool(api_key)

    def collect_candidates(self, brand_name: str, keywords: List[str], official_apps: List[Dict]) -> List[RawAppData]:
        if not self.enabled:
            raise RuntimeError("Google Play adapter not configured. Set GOOGLE_PLAY_API_KEY.")
        return []


class AppleAppStoreAdapter(AppStoreSourceAdapter):
    SOURCE_TYPE = "APPLE_APP_STORE"
    PLATFORM = "ios"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.enabled = bool(api_key)

    def collect_candidates(self, brand_name: str, keywords: List[str], official_apps: List[Dict]) -> List[RawAppData]:
        if not self.enabled:
            raise RuntimeError("Apple App Store adapter not configured. Set APP_STORE_API_KEY.")
        return []


class ImportedAppStoreAdapter(AppStoreSourceAdapter):
    SOURCE_TYPE = "IMPORTED"
    PLATFORM = "unknown"

    def __init__(self, imported_data: List[Dict]):
        self.imported_data = imported_data

    def collect_candidates(self, brand_name: str, keywords: List[str], official_apps: List[Dict]) -> List[RawAppData]:
        candidates = []
        for item in self.imported_data:
            candidates.append(RawAppData(
                app_name=item.get("app_name", ""),
                store=self.SOURCE_TYPE,
                platform=item.get("platform", "unknown"),
                app_url=item.get("app_url"),
                package_id=item.get("package_id"),
                bundle_id=item.get("bundle_id"),
                developer_name=item.get("developer_name"),
                developer_website=item.get("developer_website"),
                developer_email=item.get("developer_email"),
                app_icon_url=item.get("app_icon_url"),
                app_description=item.get("app_description"),
                short_description=item.get("short_description"),
                category=item.get("category"),
                version=item.get("version"),
                rating=item.get("rating"),
                review_count=item.get("review_count"),
                download_count=item.get("download_count"),
                external_links=item.get("external_links", []),
                raw_data=item.get("raw_data", {}),
            ))
        return candidates


def get_source_adapter(source_type: str, **kwargs) -> AppStoreSourceAdapter:
    source_type = source_type.upper()
    if source_type == "DEMO":
        return DemoAppStoreAdapter()
    elif source_type == "GOOGLE_PLAY":
        return GooglePlayStoreAdapter(kwargs.get("api_key"))
    elif source_type == "APPLE_APP_STORE":
        return AppleAppStoreAdapter(kwargs.get("api_key"))
    elif source_type == "IMPORTED":
        return ImportedAppStoreAdapter(kwargs.get("imported_data", []))
    elif source_type == "MOCK":
        return DemoAppStoreAdapter()
    else:
        raise ValueError(f"Unknown source type: {source_type}")