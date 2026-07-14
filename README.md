# 🌌 Gemini L200 Agentic Study Hub

Welcome to the **Gemini L200 Agentic Study Hub**! This application is an interactive preparation portal and visual metrics dashboard tailored specifically to help you study, practice, and conquer Google Cloud's **Gemini Enterprise L200 Partner Enablement Path**.

Built using the **Google Agent Development Kit (ADK 2.2.0)** and served via a high-performance **FastAPI** backend, the project orchestrates three distinct subagents (**Coaching**, **Teaching**, and **Quiz**) working in a coordinated learning feedback loop.

---

## 🎯 Key Features

1. **🏆 Multi-Agent Orchestration Loop (Google ADK):**
   - **The Coaching Agent:** Implicitly analyzes chat message intents and queries. If you struggle or express confusion, it automatically logs the cognitive gap to your progress database.
   - **The Teaching Agent:** Explains syllabus concepts, lists critical lesson guidelines, and provides instant navigation links to the official Google Skill Paths and Challenge Labs.
   - **The Quiz Agent:** Delivers realistic exam-accurate multiple-choice assessments dynamically tailored to your identified struggles.

2. **📊 Responsive Glassmorphic Dashboard:**
   - Visual progress ring and hours-tracker displaying "how much is left" in the curriculum.
   - An interactive vertical syllabus map of Section 1 (Development) and Section 2 (Deployment).
   - "Gaps & Struggles Map" that dynamically updates when you ask questions or fail quizzes, and auto-resolves when you pass.

3. **💾 Hybrid Database Persistence (`db_manager.py`):**
   - Integrates with **Google Cloud Firestore** for secure, cross-device multi-student persistent storage in production.
   - Automatically falls back to a **local JSON database (`l200_state.json`)** for instant offline development and testing.

4. **⚡ Ultra-Fast Environment & Container Builds (`uv`):**
   - Managed via **astral-sh/uv** for lighting-fast package resolution.
   - Fully containerized with a production-ready **Dockerfile** targeting **Google Cloud Run** standards.

---

## 📂 Project Structure

```
/home/admin_/projects/l200/
├── Dockerfile                   # Multi-stage container definition
├── requirements.txt             # FastAPI, Pydantic, and Firestore requirements
├── db_manager.py                # Dual-layer Firestore/JSON State manager
├── agent_definition.py          # Coordinated ADK subagent definitions
├── main.py                      # FastAPI server & route handlers
├── README.md                    # Instructions & architecture manual
└── static/                      # Static client-side files
    ├── index.html               # Semantic HTML Dashboard
    ├── styles.css               # Neon-cyberpunk dark theme aesthetics
    └── app.js                   # Interactive dashboard controller
```

---

## 🚀 How to Run Locally

Using **`uv`**, you can launch the application in less than 2 seconds!

```bash
# 1. Navigate to the project folder
# (From project root)
cd l200

# 2. Run the FastAPI development server
.venv/bin/python main.py
```

Once running, navigate to **`http://localhost:8080`** in your browser to explore the dashboard.

---

## 🔑 Session & Live Agent Modes

- **Local Intelligent Mode (Default):** Runs immediately without any cloud configuration. Uses smart structural routers and a predefined question bank.
- **Live Gemini Agent Mode:** Paste your **Gemini API key** in the sidebar's session key field. The backend immediately switches to an active LLM generation state, querying Gemini to generate custom explanations and write highly dynamic questions targeting your active gaps on-the-fly!

---

## ☁️ Infrastructure as Code (IaC) with Terraform

A production-grade, highly secure Terraform configuration is provided in the repository to automate provisioning of all required cloud assets:

* **`main.tf`**: Configures Cloud Run (fully containerized microservice), Artifact Registry docker repo, Firestore Native instance, and Secret Manager bindings.
* **`variables.tf`**: Exposes parameters like `project_id`, `region`, and service labels.
* **`outputs.tf`**: Outputs secure public HTTPS endpoints and registry paths.

### 🚀 Provisioning Steps:
1. Initialize Terraform provider:
   ```bash
   terraform init
   ```
2. Create and fill a `terraform.tfvars` (copying the provided example):
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars and add your GCP project_id
   ```
3. Run a planning phase to preview creations:
   ```bash
   terraform plan -out=tfplan
   ```
4. Securely apply resources:
   ```bash
   terraform apply tfplan
   ```

---

## 🔑 Secure Secret Management & Secret Manager Integration

The application securely avoids hardcoded API keys by employing a hierarchical programmatic credential loader:

1. **Client Header Input:** Fetches from the interactive web console.
2. **Environment Variable Fallback:** Reads `GEMINI_API_KEY` from system env variables.
3. **Google Secret Manager (Programmatic Fallback):** Programmatically resolves the API key by querying Google Secret Manager via `google-cloud-secret-manager` API:
   ```python
   # Programmatic resolution in main.py
   client = secretmanager.SecretManagerServiceClient()
   name = f"projects/{project_id}/secrets/gemini-api-key/versions/latest"
   response = client.access_secret_version(request={"name": name})
   ```

---

## 🛠️ Deployment with ADK / Agent CLI

The Gemini L200 Study Hub is fully compliant with Google ADK packaging specifications. To deploy the microservice to **Vertex AI Agent Engine (Agent Platform)** using the **ADK CLI**:

1. Stage source code to a clean build directory:
   ```bash
   mkdir -p l200_staging
   cp agent.py agent_definition.py db_manager.py main.py l200_staging/
   ```
2. Deploy directly using the `adk deploy` tool:
   ```bash
   adk deploy agent_engine \
     --project=your-gcp-project-id \
     --region=us-central1 \
     --display_name="L200 Study Orchestrator" \
     l200_staging/
   ```

---

*Powered by Google Antigravity & the Google Agent Development Kit.*

