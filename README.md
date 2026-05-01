# 🩺 Auto-Chart: Fax-to-FHIR Pipeline

This is an automated clinical data extraction engine designed to bridge the gap between legacy document ingestion workflows common in healthcare settings and modern data standards. The system monitors an ingestion point for unstructured medical documents (Images/PDFs), transforms them into clean Markdown, and utilizes AI agents to map the content into validated **FHIR R5** resources.

---

## 🌟 Key Features

*   **Event-Driven Ingestion:** Real-time monitoring of document arrival via filesystem observers (Watchdogs).
*   **Intelligent Extraction:** Utilizes `Docling` for high-fidelity PDF-to-Markdown parsing.
*   **Agentic Mapping:** Leverages `PydanticAI` for structured, type-safe extraction from unstructured text.
*   **FHIR Compliance:** Ensures all output data strictly adheres to FHIR R5 schemas.

---

## 🏗️ System Architecture

The system follows a modular, containerized design to ensure the ingestion layer remains decoupled from the processing logic. This allows for horizontal scaling and high availability depending on the deployment environment.

> [!TIP]
> For a visual breakdown of the container interactions and data flow, see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## 🛠️ Core Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Ingestion** | SFTP / File Observer | Handles document receiving and event triggers |
| **Parsing** | [Docling](https://github.com/DS4SD/docling) | Document layout analysis and text extraction |
| **Orchestration** | [PydanticAI](https://github.com/pydantic/pydantic-ai) | AI Agent logic and model validation |
| **Inference** | Gemini 2.5 Flash | Semantic understanding and entity extraction |
| **Data Model** | FHIR R5 | Industry-standard clinical data interoperability |
