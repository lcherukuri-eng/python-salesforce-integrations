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

### Analytics

- Account Data Quality Analysis
- Missing Data Detection
- Duplicate Name Detection
- Data Completeness Metrics

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
    ↓
Pandas
    ↓
Data Quality Analysis
    ↓
CSV Export
    ↓
AWS S3