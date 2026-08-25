# Python Salesforce Integrations

A headless Salesforce integration platform built using Python, FastAPI, OAuth 2.0 PKCE, Pandas, and AWS S3.

## Technologies

- Python
- FastAPI
- Salesforce REST API
- OAuth 2.0 PKCE
- Pandas
- JSON
- AWS S3
- boto3

## Features

- Salesforce OAuth 2.0 Authentication
- PKCE Authorization Flow
- Account Data Extraction
- CSV Export using Pandas
- AWS S3 File Upload
- Headless Salesforce Integration

## Architecture

```text
Salesforce
    ↓
OAuth 2.0 + PKCE
    ↓
FastAPI
    ↓
Pandas
    ↓
CSV Export
    ↓
AWS S3
