"""Configurable technology taxonomy with aliases."""

from __future__ import annotations

TAXONOMY: list[dict] = [
    {"canonical_name": "Java", "category": "programming_languages", "aliases": ["java"]},
    {"canonical_name": "Kotlin", "category": "programming_languages", "aliases": ["kotlin"]},
    {"canonical_name": "Python", "category": "programming_languages", "aliases": ["python"]},
    {
        "canonical_name": "TypeScript",
        "category": "programming_languages",
        "aliases": ["typescript", "ts"],
    },
    {
        "canonical_name": "JavaScript",
        "category": "programming_languages",
        "aliases": ["javascript", "js", "node.js", "nodejs"],
    },
    {"canonical_name": "Go", "category": "programming_languages", "aliases": ["golang", "go lang"]},
    {"canonical_name": "Rust", "category": "programming_languages", "aliases": ["rust"]},
    {"canonical_name": "C#", "category": "programming_languages", "aliases": ["c#", "csharp", ".net"]},
    {
        "canonical_name": "Spring Boot",
        "category": "backend_frameworks",
        "aliases": ["spring boot", "springboot"],
    },
    {"canonical_name": "Quarkus", "category": "backend_frameworks", "aliases": ["quarkus"]},
    {"canonical_name": "Node.js", "category": "backend_frameworks", "aliases": ["node", "nodejs"]},
    {"canonical_name": "React", "category": "frontend_frameworks", "aliases": ["react", "react.js"]},
    {"canonical_name": "Angular", "category": "frontend_frameworks", "aliases": ["angular"]},
    {
        "canonical_name": "PostgreSQL",
        "category": "databases",
        "aliases": ["postgres", "postgresql", "psql"],
    },
    {"canonical_name": "Oracle", "category": "databases", "aliases": ["oracle"]},
    {"canonical_name": "MongoDB", "category": "databases", "aliases": ["mongodb", "mongo"]},
    {"canonical_name": "Redis", "category": "databases", "aliases": ["redis"]},
    {"canonical_name": "Kafka", "category": "messaging", "aliases": ["kafka", "apache kafka"]},
    {"canonical_name": "RabbitMQ", "category": "messaging", "aliases": ["rabbitmq", "rabbit mq"]},
    {"canonical_name": "AWS", "category": "cloud_providers", "aliases": ["amazon web services", "aws"]},
    {"canonical_name": "Azure", "category": "cloud_providers", "aliases": ["microsoft azure", "azure"]},
    {"canonical_name": "GCP", "category": "cloud_providers", "aliases": ["google cloud", "gcp"]},
    {
        "canonical_name": "Kubernetes",
        "category": "orchestration",
        "aliases": ["kubernetes", "k8s"],
    },
    {"canonical_name": "Docker", "category": "containers", "aliases": ["docker"]},
    {"canonical_name": "Terraform", "category": "iac", "aliases": ["terraform"]},
    {"canonical_name": "Helm", "category": "orchestration", "aliases": ["helm"]},
    {"canonical_name": "Argo CD", "category": "devops", "aliases": ["argo cd", "argocd"]},
    {
        "canonical_name": "GitHub Actions",
        "category": "devops",
        "aliases": ["github actions", "gh actions"],
    },
    {"canonical_name": "Prometheus", "category": "observability", "aliases": ["prometheus"]},
    {"canonical_name": "Grafana", "category": "observability", "aliases": ["grafana"]},
    {
        "canonical_name": "OpenTelemetry",
        "category": "observability",
        "aliases": ["opentelemetry", "otel"],
    },
    {"canonical_name": "LangChain", "category": "llm_frameworks", "aliases": ["langchain"]},
    {"canonical_name": "LlamaIndex", "category": "llm_frameworks", "aliases": ["llamaindex"]},
    {"canonical_name": "LangGraph", "category": "llm_frameworks", "aliases": ["langgraph"]},
    {"canonical_name": "Ollama", "category": "llm_frameworks", "aliases": ["ollama"]},
    {"canonical_name": "vLLM", "category": "llm_frameworks", "aliases": ["vllm"]},
    {"canonical_name": "RAG", "category": "rag", "aliases": ["retrieval augmented generation", "rag"]},
    {"canonical_name": "pgvector", "category": "vector_databases", "aliases": ["pgvector"]},
    {"canonical_name": "Qdrant", "category": "vector_databases", "aliases": ["qdrant"]},
    {"canonical_name": "Weaviate", "category": "vector_databases", "aliases": ["weaviate"]},
    {"canonical_name": "Milvus", "category": "vector_databases", "aliases": ["milvus"]},
    {"canonical_name": "MLflow", "category": "mlops", "aliases": ["mlflow"]},
    {"canonical_name": "FastAPI", "category": "backend_frameworks", "aliases": ["fastapi"]},
    {"canonical_name": "Next.js", "category": "frontend_frameworks", "aliases": ["nextjs", "next.js"]},
]


def build_alias_index(items: list[dict] | None = None) -> dict[str, str]:
    index: dict[str, str] = {}
    for item in items or TAXONOMY:
        canonical = item["canonical_name"]
        index[canonical.lower()] = canonical
        for alias in item.get("aliases", []):
            index[alias.lower()] = canonical
    return index
