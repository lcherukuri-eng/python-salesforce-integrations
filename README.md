# Python Salesforce Integrations

A headless Salesforce integration platform built using Python, FastAPI, Salesforce APIs, Pandas, and AWS S3.

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
- Data Stream ingestion for Account, Contact, and Opportunity
- Data Cloud Token Exchange
- Data Cloud Query API integration
- Data Cloud Ingestion API Integration
- Customer Search APIs
- Customer Context APIs
- Customer Insights APIs
- Calculated Insights APIs
- Identity Resolution Integration
- Unified Individual APIs
- Unified Contact Point Email APIs
- Customer 360 APIs
- Website Engagement DMO Integration
- Website Engagement Event Tracking
- Clickstream Event Ingestion and Retrieval

### AI Pipeline Analysis
- Claude Integration
- AI-generated Executive Pipeline Summaries
- Pipeline Risk and Opportunity Analysis
- Revenue Pipeline Recommendations

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
