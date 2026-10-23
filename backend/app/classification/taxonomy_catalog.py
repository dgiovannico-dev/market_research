"""Technology taxonomy entries (canonical name + category + aliases).

Kept separate from ``taxonomy.py`` so the alias index helpers stay thin.
Matching uses word-boundary aliases; avoid ultra-ambiguous 1–2 letter tokens
(``c``, ``r``, ``go`` alone is already risky — prefer ``golang`` where possible).
"""

from __future__ import annotations

# Existing core stack (software engineering foundation).
_CORE: list[dict] = [
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
        "aliases": ["javascript", "js", "ecmascript"],
    },
    {
        "canonical_name": "Go",
        "category": "programming_languages",
        "aliases": ["golang", "go lang"],
    },
    {"canonical_name": "Rust", "category": "programming_languages", "aliases": ["rust"]},
    {
        "canonical_name": "C#",
        "category": "programming_languages",
        "aliases": ["c#", "csharp", ".net", "dotnet", "asp.net"],
    },
    {
        "canonical_name": "C++",
        "category": "programming_languages",
        "aliases": ["c++", "cpp", "cplusplus"],
    },
    {"canonical_name": "Scala", "category": "programming_languages", "aliases": ["scala"]},
    {"canonical_name": "Ruby", "category": "programming_languages", "aliases": ["ruby", "rails"]},
    {"canonical_name": "PHP", "category": "programming_languages", "aliases": ["php"]},
    {"canonical_name": "Swift", "category": "programming_languages", "aliases": ["swift"]},
    {"canonical_name": "Dart", "category": "programming_languages", "aliases": ["dart"]},
    {
        "canonical_name": "Spring Boot",
        "category": "backend_frameworks",
        "aliases": ["spring boot", "springboot", "spring"],
    },
    {"canonical_name": "Quarkus", "category": "backend_frameworks", "aliases": ["quarkus"]},
    {
        "canonical_name": "Node.js",
        "category": "backend_frameworks",
        "aliases": ["node.js", "nodejs", "node js"],
    },
    {"canonical_name": "FastAPI", "category": "backend_frameworks", "aliases": ["fastapi"]},
    {"canonical_name": "Django", "category": "backend_frameworks", "aliases": ["django"]},
    {"canonical_name": "Flask", "category": "backend_frameworks", "aliases": ["flask"]},
    {"canonical_name": "NestJS", "category": "backend_frameworks", "aliases": ["nestjs", "nest.js"]},
    {
        "canonical_name": "Express",
        "category": "backend_frameworks",
        "aliases": ["express", "express.js", "expressjs"],
    },
    {"canonical_name": "React", "category": "frontend_frameworks", "aliases": ["react", "react.js"]},
    {"canonical_name": "Angular", "category": "frontend_frameworks", "aliases": ["angular"]},
    {"canonical_name": "Vue", "category": "frontend_frameworks", "aliases": ["vue", "vue.js", "vuejs"]},
    {"canonical_name": "Svelte", "category": "frontend_frameworks", "aliases": ["svelte", "sveltekit"]},
    {
        "canonical_name": "Next.js",
        "category": "frontend_frameworks",
        "aliases": ["nextjs", "next.js"],
    },
    {
        "canonical_name": "React Native",
        "category": "mobile",
        "aliases": ["react native", "react-native"],
    },
    {"canonical_name": "Flutter", "category": "mobile", "aliases": ["flutter"]},
    {
        "canonical_name": "PostgreSQL",
        "category": "databases",
        "aliases": ["postgres", "postgresql", "psql"],
    },
    {"canonical_name": "MySQL", "category": "databases", "aliases": ["mysql", "mariadb"]},
    {"canonical_name": "Oracle", "category": "databases", "aliases": ["oracle"]},
    {"canonical_name": "MongoDB", "category": "databases", "aliases": ["mongodb", "mongo"]},
    {"canonical_name": "Redis", "category": "databases", "aliases": ["redis"]},
    {
        "canonical_name": "Elasticsearch",
        "category": "databases",
        "aliases": ["elasticsearch", "elastic search", "opensearch"],
    },
    {"canonical_name": "Cassandra", "category": "databases", "aliases": ["cassandra"]},
    {"canonical_name": "DynamoDB", "category": "databases", "aliases": ["dynamodb", "dynamo db"]},
    {"canonical_name": "Kafka", "category": "messaging", "aliases": ["kafka", "apache kafka"]},
    {"canonical_name": "RabbitMQ", "category": "messaging", "aliases": ["rabbitmq", "rabbit mq"]},
    {
        "canonical_name": "GraphQL",
        "category": "apis",
        "aliases": ["graphql", "graph ql"],
    },
    {"canonical_name": "gRPC", "category": "apis", "aliases": ["grpc", "g-rpc"]},
    {
        "canonical_name": "AWS",
        "category": "cloud_providers",
        "aliases": ["amazon web services", "aws"],
    },
    {
        "canonical_name": "Azure",
        "category": "cloud_providers",
        "aliases": ["microsoft azure", "azure"],
    },
    {
        "canonical_name": "GCP",
        "category": "cloud_providers",
        "aliases": ["google cloud", "google cloud platform", "gcp"],
    },
    {
        "canonical_name": "Kubernetes",
        "category": "orchestration",
        "aliases": ["kubernetes", "k8s"],
    },
    {"canonical_name": "Docker", "category": "containers", "aliases": ["docker", "containerd"]},
    {"canonical_name": "Terraform", "category": "iac", "aliases": ["terraform", "tf"]},
    {"canonical_name": "Pulumi", "category": "iac", "aliases": ["pulumi"]},
    {"canonical_name": "Ansible", "category": "iac", "aliases": ["ansible"]},
    {"canonical_name": "Helm", "category": "orchestration", "aliases": ["helm"]},
    {"canonical_name": "Istio", "category": "orchestration", "aliases": ["istio", "service mesh"]},
    {"canonical_name": "Argo CD", "category": "devops", "aliases": ["argo cd", "argocd"]},
    {
        "canonical_name": "GitHub Actions",
        "category": "devops",
        "aliases": ["github actions", "gh actions"],
    },
    {
        "canonical_name": "GitLab CI",
        "category": "devops",
        "aliases": ["gitlab ci", "gitlab-ci", "gitlab ci/cd"],
    },
    {"canonical_name": "Jenkins", "category": "devops", "aliases": ["jenkins"]},
    {"canonical_name": "Prometheus", "category": "observability", "aliases": ["prometheus"]},
    {"canonical_name": "Grafana", "category": "observability", "aliases": ["grafana"]},
    {
        "canonical_name": "OpenTelemetry",
        "category": "observability",
        "aliases": ["opentelemetry", "otel"],
    },
    {"canonical_name": "Datadog", "category": "observability", "aliases": ["datadog"]},
    {"canonical_name": "Nginx", "category": "networking", "aliases": ["nginx"]},
]

_DATA_PLATFORM: list[dict] = [
    {"canonical_name": "Spark", "category": "data_engineering", "aliases": ["apache spark", "spark"]},
    {"canonical_name": "Flink", "category": "data_engineering", "aliases": ["apache flink", "flink"]},
    {"canonical_name": "Airflow", "category": "data_engineering", "aliases": ["airflow", "apache airflow"]},
    {"canonical_name": "dbt", "category": "data_engineering", "aliases": ["dbt", "data build tool"]},
    {"canonical_name": "Snowflake", "category": "data_warehouses", "aliases": ["snowflake"]},
    {
        "canonical_name": "BigQuery",
        "category": "data_warehouses",
        "aliases": ["bigquery", "big query", "google bigquery"],
    },
    {"canonical_name": "Databricks", "category": "data_platforms", "aliases": ["databricks"]},
    {"canonical_name": "DuckDB", "category": "databases", "aliases": ["duckdb", "duck db"]},
    {"canonical_name": "Pandas", "category": "data_science", "aliases": ["pandas"]},
    {"canonical_name": "Polars", "category": "data_science", "aliases": ["polars"]},
    {"canonical_name": "Kafka Streams", "category": "messaging", "aliases": ["kafka streams"]},
]

_AI_ML: list[dict] = [
    {"canonical_name": "LangChain", "category": "llm_frameworks", "aliases": ["langchain"]},
    {"canonical_name": "LlamaIndex", "category": "llm_frameworks", "aliases": ["llamaindex", "llama index"]},
    {"canonical_name": "LangGraph", "category": "llm_frameworks", "aliases": ["langgraph"]},
    {"canonical_name": "Ollama", "category": "llm_frameworks", "aliases": ["ollama"]},
    {"canonical_name": "vLLM", "category": "llm_frameworks", "aliases": ["vllm"]},
    {
        "canonical_name": "RAG",
        "category": "rag",
        "aliases": ["retrieval augmented generation", "retrieval-augmented generation", "rag"],
    },
    {"canonical_name": "pgvector", "category": "vector_databases", "aliases": ["pgvector"]},
    {"canonical_name": "Qdrant", "category": "vector_databases", "aliases": ["qdrant"]},
    {"canonical_name": "Weaviate", "category": "vector_databases", "aliases": ["weaviate"]},
    {"canonical_name": "Milvus", "category": "vector_databases", "aliases": ["milvus"]},
    {"canonical_name": "Pinecone", "category": "vector_databases", "aliases": ["pinecone"]},
    {"canonical_name": "Chroma", "category": "vector_databases", "aliases": ["chromadb", "chroma"]},
    {"canonical_name": "MLflow", "category": "mlops", "aliases": ["mlflow"]},
    {"canonical_name": "PyTorch", "category": "ml_frameworks", "aliases": ["pytorch", "torch"]},
    {
        "canonical_name": "TensorFlow",
        "category": "ml_frameworks",
        "aliases": ["tensorflow", "tf.keras", "keras"],
    },
    {
        "canonical_name": "Hugging Face",
        "category": "ml_frameworks",
        "aliases": ["hugging face", "huggingface", "transformers"],
    },
    {
        "canonical_name": "Scikit-learn",
        "category": "ml_frameworks",
        "aliases": ["scikit-learn", "sklearn", "scikit learn"],
    },
    {"canonical_name": "XGBoost", "category": "ml_frameworks", "aliases": ["xgboost"]},
    {
        "canonical_name": "LLM",
        "category": "ai",
        "aliases": ["large language model", "large language models", "llm", "llms"],
    },
    {
        "canonical_name": "Generative AI",
        "category": "ai",
        "aliases": ["generative ai", "genai", "gen ai"],
    },
    {
        "canonical_name": "Prompt Engineering",
        "category": "ai",
        "aliases": ["prompt engineering", "prompt engineer"],
    },
    {
        "canonical_name": "Fine-tuning",
        "category": "ai",
        "aliases": ["fine-tuning", "finetuning", "fine tuning", "lora", "qlora"],
    },
    {
        "canonical_name": "AI Agents",
        "category": "ai",
        "aliases": ["ai agent", "ai agents", "autonomous agent", "agentic"],
    },
    {"canonical_name": "CrewAI", "category": "llm_frameworks", "aliases": ["crewai", "crew ai"]},
    {"canonical_name": "AutoGen", "category": "llm_frameworks", "aliases": ["autogen", "microsoft autogen"]},
    {
        "canonical_name": "Semantic Kernel",
        "category": "llm_frameworks",
        "aliases": ["semantic kernel"],
    },
    {
        "canonical_name": "OpenAI",
        "category": "ai_platforms",
        "aliases": ["openai", "gpt-4", "gpt-4o", "chatgpt"],
    },
    {
        "canonical_name": "Anthropic",
        "category": "ai_platforms",
        "aliases": ["anthropic", "claude"],
    },
    {
        "canonical_name": "Azure OpenAI",
        "category": "ai_platforms",
        "aliases": ["azure openai", "azure open ai"],
    },
    {
        "canonical_name": "AWS Bedrock",
        "category": "ai_platforms",
        "aliases": ["bedrock", "amazon bedrock", "aws bedrock"],
    },
    {
        "canonical_name": "Vertex AI",
        "category": "ai_platforms",
        "aliases": ["vertex ai", "vertexai", "google vertex"],
    },
    {
        "canonical_name": "SageMaker",
        "category": "ai_platforms",
        "aliases": ["sagemaker", "amazon sagemaker", "aws sagemaker"],
    },
    {"canonical_name": "CUDA", "category": "ml_infra", "aliases": ["cuda", "nvidia cuda"]},
    {
        "canonical_name": "Computer Vision",
        "category": "ai",
        "aliases": ["computer vision", "cv engineer", "opencv"],
    },
    {"canonical_name": "NLP", "category": "ai", "aliases": ["natural language processing", "nlp"]},
    {
        "canonical_name": "MLOps",
        "category": "mlops",
        "aliases": ["mlops", "ml ops", "machine learning ops"],
    },
]

_SECURITY: list[dict] = [
    {
        "canonical_name": "Cybersecurity",
        "category": "security",
        "aliases": ["cybersecurity", "cyber security", "infosec", "information security"],
    },
    {
        "canonical_name": "AppSec",
        "category": "security",
        "aliases": ["appsec", "application security", "secure coding"],
    },
    {
        "canonical_name": "DevSecOps",
        "category": "security",
        "aliases": ["devsecops", "dev sec ops", "shift-left security"],
    },
    {
        "canonical_name": "Penetration Testing",
        "category": "security",
        "aliases": ["penetration testing", "pentest", "pen test", "red team"],
    },
    {
        "canonical_name": "SOC",
        "category": "security",
        "aliases": ["security operations center", "soc analyst", "soc"],
    },
    {"canonical_name": "SIEM", "category": "security", "aliases": ["siem"]},
    {"canonical_name": "SOAR", "category": "security", "aliases": ["soar"]},
    {"canonical_name": "EDR", "category": "security", "aliases": ["edr", "endpoint detection"]},
    {"canonical_name": "XDR", "category": "security", "aliases": ["xdr"]},
    {"canonical_name": "WAF", "category": "security", "aliases": ["waf", "web application firewall"]},
    {
        "canonical_name": "Zero Trust",
        "category": "security",
        "aliases": ["zero trust", "zero-trust"],
    },
    {
        "canonical_name": "IAM",
        "category": "security",
        "aliases": ["identity and access management", "iam", "privileged access"],
    },
    {"canonical_name": "OAuth", "category": "security", "aliases": ["oauth", "oauth2", "oauth 2"]},
    {"canonical_name": "OIDC", "category": "security", "aliases": ["oidc", "openid connect"]},
    {"canonical_name": "SAML", "category": "security", "aliases": ["saml"]},
    {
        "canonical_name": "HashiCorp Vault",
        "category": "security",
        "aliases": ["hashicorp vault", "vault secrets"],
    },
    {"canonical_name": "Snyk", "category": "security", "aliases": ["snyk"]},
    {
        "canonical_name": "SonarQube",
        "category": "security",
        "aliases": ["sonarqube", "sonar qube", "sonarcloud"],
    },
    {"canonical_name": "OWASP", "category": "security", "aliases": ["owasp", "owasp top 10"]},
    {"canonical_name": "Splunk", "category": "security", "aliases": ["splunk"]},
    {
        "canonical_name": "CrowdStrike",
        "category": "security",
        "aliases": ["crowdstrike", "falcon"],
    },
    {"canonical_name": "Trivy", "category": "security", "aliases": ["trivy"]},
    {"canonical_name": "Falco", "category": "security", "aliases": ["falco"]},
    {"canonical_name": "Checkov", "category": "security", "aliases": ["checkov"]},
    {
        "canonical_name": "Threat Modeling",
        "category": "security",
        "aliases": ["threat modeling", "threat model", "stride"],
    },
    {
        "canonical_name": "Cryptography",
        "category": "security",
        "aliases": ["cryptography", "crypto engineer", "pki", "mtls"],
    },
    {
        "canonical_name": "Cloud Security",
        "category": "security",
        "aliases": ["cloud security", "cspm", "cwpp", "cloudsec"],
    },
    {
        "canonical_name": "Network Security",
        "category": "security",
        "aliases": ["network security", "ids/ips", "intrusion detection"],
    },
]

TAXONOMY_ENTRIES: list[dict] = [*_CORE, *_DATA_PLATFORM, *_AI_ML, *_SECURITY]
