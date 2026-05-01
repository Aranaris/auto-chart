# Auto-Chart System Architecture

This document outlines the architecture for the OCR-to-FHIR pipeline, optimized for using Docker and PydanticAI.

## 1. System Overview

The system automates the extraction of patient data from faxed or uploaded documents/images and maps them into FHIR-compliant JSON resources.
```mermaid
graph TD
    %% Global Styling for Dark Mode
    accTitle: Auto-Chart Dark Mode Architecture
    direction TB

    %% Node Definitions with Classes
    subgraph External_Sources ["External Sources"]
        User((Fax/Image Upload))
        LLM[Gemini 2.5 Flash API]
        DEST[Final Destination]
    end

    subgraph Local_Services ["Backend Server"]
        direction TB
        SFTP[SFTPGo Container]
        STORAGE[(Shared Volume)]
        OCR[OCR Service: Docling + PydanticAI]
        
        SFTP -- "Write File" --> STORAGE
        STORAGE -- "Watchdog" --> OCR
    end

    %% Cross-Subgraph Connections
    User -- "<b><font color='#7289da'>UPLOAD PDF</font></b>" --> SFTP
    OCR <--> LLM
    OCR -- "<b><font color='#7289da'>POST FHIR JSON</font></b>" --> DEST

    %% Class Definitions (Dark Mode Optimized)
    classDef external fill:#1a1a1a,stroke:#7289da,stroke-width:2px,color:#fff;
    classDef container fill:#2d2d2d,stroke:#00ffc8,stroke-width:2px,color:#fff;
    classDef storage fill:#2d2d2d,stroke:#f0db4f,stroke-width:2px,color:#fff;

    %% Apply Classes
    class User,LLM,DEST external;
    class SFTP,OCR container;
    class STORAGE storage;
    
    %% Style adjustments for the Subgraph Headers
    style External_Sources fill:#121212,stroke:#444,stroke-dasharray: 5 5,color:#aaa
    style Local_Services fill:#121212,stroke:#444,stroke-dasharray: 5 5,color:#aaa

    %% Link Styling (Makes the arrows thicker/brighter)
    linkStyle default stroke:#888,stroke-width:2px;
    linkStyle 0,1,2,3,4 stroke-width:3px;
```
