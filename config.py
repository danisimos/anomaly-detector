import os

from dotenv import load_dotenv

load_dotenv()


def _str(env_key: str, default: str) -> str:
    return os.environ.get(env_key, default)


def _int(env_key: str, default: int) -> int:
    return int(os.environ.get(env_key, str(default)))


def _bool(env_key: str, default: bool) -> bool:
    return os.environ.get(env_key, str(default)).lower() in ("true", "t", "1")


class Config:
    PROMETHEUS_URL: str = _str(
        "PROMETHEUS_URL",
        default="localhost:9090",
    )

    PROMETHEUS_QUERY_CPU: str = _str(
        "PROMETHEUS_QUERY_CPU",
        default="sum (rate(container_cpu_usage_seconds_total{name=~\"^k8s_.*\"}[10m]))",
    )

    PROMETHEUS_QUERY_MEMORY: str = _str(
        "PROMETHEUS_QUERY_MEMORY",
        default="sum (container_memory_working_set_bytes{id!=\"/\",kubernetes_io_hostname=~\"cl1i6ek5us1gmcv87dql-oqaz\",pod_name=~\"^()()().*$\"})",
    )

    TELEGRAM_API_KEY: str = _str(
        "TELEGRAM_API_KEY",
        default="7093463585:AAG6ARarInDNj2aiy8eTY_UgMSRTvuwo6bQ",
    )


def get_config() -> Config:
    return Config()
