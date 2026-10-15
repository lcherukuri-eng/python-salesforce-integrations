# Customer Intelligence Platform

An AI-powered customer intelligence platform built with Python, FastAPI, Salesforce Data Cloud, MCP, Claude AI, and AWS. The platform combines Customer 360 data, segmentation, behavioral analytics, calculated insights, and AI-driven recommendations to provide actionable customer intelligence.

## Technologies
- Python
- FastAPI
- Salesforce REST API
- Salesforce Bulk API 2.0
- Salesforce Data Cloud
- Salesforce Platform Events
- Salesforce Pub/Sub API
- OAuth 2.0
- PKCE
- gRPC
- Protocol Buffers (Protobuf)
- Pandas
- AWS S3
- boto3
- fastavro
- Claude
- OpenAI
- PostgreSQL
- pgvector
- LangChain
- LangGraph
- MCP (Model Context Protocol)

## Features

### Authentication
- Authorization Code Flow with PKCE
- Refresh Token Support
- Token Persistence
- Client Credentials Flow

### Salesforce Integrations
- Account Data Retrieval
- CSV Export
- AWS S3 Upload
- Bulk API 2.0 Export

### Event-Driven Integration
- Salesforce Platform Events
- Salesforce Pub/Sub API Consumer
- gRPC-based Event Subscription
- Protocol Buffers (Protobuf)
- Avro Payload Decoding
- Schema Retrieval with GetSchema
- Schema Caching
- Replay ID Checkpointing
- Replay Recovery
- Automatic Reconnection Handling
- Event Processing Pipeline
- Apache Kafka Integration
- Kafka Producer
- Kafka Consumer
- Kafka Topics
- Consumer Groups
- Event Streaming Architecture

### Data Cloud Integration
- Data Stream Ingestion (Account, Contact, Opportunity)
- Data Cloud Token Exchange
- Data Cloud Query API
- Data Cloud Ingestion API
- Identity Resolution
- Unified Individual APIs
- Unified Contact Point Email APIs
- Customer 360 APIs
- Calculated Insights Integration
- Data Cloud Segmentation
- Website Engagement DMO Integration
- Website Engagement Event Tracking
- Clickstream Event Ingestion and Retrieval

### AI-Powered Customer Intelligence
- Customer 360 Account Intelligence
- Health Score and Health Status
- Opportunity Timeline Generation
- Website Engagement Activity Analysis
- Segment Classification
- AI Risk Assessment
- Confidence Scoring
- Next Best Action Recommendations
- AI-generated Executive Pipeline Summaries
- Opportunity Risk Analysis
- Revenue Pipeline Recommendations
- Claude-powered Customer Intelligence
- Async Anthropic API Integration
- Async FastAPI AI Endpoints

### Retrieval-Augmented Generation (RAG)
- OpenAI Embeddings
- PostgreSQL with pgvector
- Semantic Vector Search
- PostgreSQL Full-Text Search
- Hybrid Search using Vector Similarity and Text Ranking
- Customer ID Metadata Filtering
- Retrieval-Augmented Generation (RAG)
- LangChain Prompt Templates
- LangChain Document and Metadata Handling
- Custom LangChain Hybrid Retriever
- Async LangChain RAG Pipeline
- LangGraph Workflow Orchestration
- Relevance-Based Conditional Routing
- Fallback Handling for Low-Relevance Retrieval
- Claude-powered Grounded Response Generation
- Async FastAPI RAG Endpoint

### MCP Integration
- Model Context Protocol (MCP) Server
- Claude Desktop Integration
- Customer 360 MCP Tools
- Customer Intelligence MCP Tools
- Event Ingestion MCP Tools
- AI-powered Customer Interaction Workflows

### Analytics
- Account Data Quality Analysis
- Missing Data Detection
- Duplicate Name Detection
- Data Completeness Metrics

### Cloud Deployment
- FastAPI deployed on Render

### Backend Features
- FastAPI Background Tasks
- Reusable DataFrame Services
- Environment-based Configuration

## Architecture

```text
Salesforce
    ↓
OAuth 2.0
    ├── Authorization Code + PKCE
    └── Client Credentials
    ↓
FastAPI
    ├── Salesforce REST APIs
    ├── Data Cloud Query API
    ├── Data Cloud Ingestion API
    ├── Claude AI
    └── Pub/Sub Consumer
            ↓
        Platform Events
            ↓
        gRPC / Protobuf
            ↓
        Replay Recovery
            ↓
        Avro Decoding
            ↓
        Event Processing
    
    ↓
    ├── Pandas
    │   ↓
    │   Data Quality Analysis
    │   ↓
    │   CSV Export
    │   ↓
    │   AWS S3
    │
    └── Data Cloud
        ├── Identity Resolution
        ├── Unified Individual
        ├── Calculated Insights
        └── Website Engagement Events
```

### RAG Architecture

```text
User Query
    ↓
FastAPI RAG Endpoint
    ↓
LangGraph Workflow
    ↓
Retrieve Node  
    ↓
LangChain Hybrid Retriever
    ↓
Hybrid Search
    ├── OpenAI Query Embedding
    │       ↓
    │   pgvector Similarity Search
    │
    └── PostgreSQL Full-Text Search
              ↓
         Hybrid Ranking
              ↓
      LangChain Documents
              ↓
       Relevance Check
          ┌────┴─────┐
          ↓          ↓
      Relevant   Low Relevance
          ↓          ↓
    Generate Node  Fallback
          ↓          ↓
      LangChain     END
          ↓
      Claude AI
          ↓
    Grounded Answer
          ↓
         END
          ↓
    API Response
```
