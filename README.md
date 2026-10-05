# ADR Governance Studio 🏛️

**ADR Governance Studio** is an enterprise-grade solution for managing, linting, and visualizing **Architecture Decision Records (ADRs)** directly within Git workflows. It bridges developer-centric Markdown files in version control with executive-level architecture governance, dependency graphing, and CI/CD compliance guardrails. Test

---

## 🌟 Key Features

* **⚡ Native Go CLI (`adr-cli`)**: Single-binary executable to initialize, generate, link, and validate ADR files locally using YAML frontmatter schema validation.
* **🛡️ CI/CD & Enterprise Linter**: Automated GitHub Action / GitLab CI pipeline gate that enforces required tags, status lifecycles, trade-off descriptions, and breaking change rules during Pull Requests.
* **📊 Visual Decision Graph & Kanban Dashboard**: Interactive web UI featuring an SVG/React Flow dependency graph (`supersedes`, `relates_to`, `depends_on`) and drag-and-drop Kanban lifecycle management.
* **🤖 AI Architecture Assistant & Drafter**: RAG-powered query engine to search historical architectural decisions in natural language and automatically draft ADR Markdown files from meeting notes.
* **🔐 Enterprise GitHub App Integration**: Webhook-driven bot featuring OAuth2 authentication, GitHub Check Runs API annotations, and enterprise rule policy enforcement.

---

## 📁 Repository Structure

```text
adr-governance-studio/
├── .adr/                       # Local ADR storage & rule configuration
│   ├── decisions/              # Markdown ADR files (e.g., 0001-event-architecture.md)
│   └── governance.json         # Enterprise compliance policy rules
├── cli/                        # Native Go CLI source code (`main.go`)
├── backend/                    # Python FastAPI server for Webhooks & AI Assistant
├── web/                        # Web UI Dashboard & Decision Graph (`index.html`)
├── .github/
│   └── workflows/
│       └── adr-governance.yml  # GitHub Actions CI/CD pipeline workflow
└── README.md                   # Repository documentation
