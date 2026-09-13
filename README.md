# Customer Intelligence Platform

An AI-powered customer intelligence platform built with Python, FastAPI, Salesforce Data Cloud, MCP, Claude AI, and AWS. The platform combines Customer 360 data, segmentation, behavioral analytics, calculated insights, and AI-driven recommendations to provide actionable customer intelligence.

## Technologies
- Python
- FastAPI
- Salesforce REST API
- Salesforce Bulk API 2.0
- OAuth 2.0
- PKCE
- Pandas
- AWS S3
- boto3
- Salesforce Data Cloud
- Claude
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
    └── Claude AI
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
