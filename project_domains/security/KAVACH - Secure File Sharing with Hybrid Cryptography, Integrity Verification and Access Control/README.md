# KAVACH: Secure File Sharing with Hybrid Cryptography, Integrity Verification and Access Control

KAVACH is a Django-based secure file sharing project designed for academic implementation. It combines hybrid cryptography, user-specific key management, integrity verification, access control, audit logging, and suspicious activity detection in one platform.

## Main Objective

To build a secure file sharing system where files are encrypted before storage, shared only with authorized users, verified for integrity, and monitored through audit logs.

## Core Techniques

- AES encryption for file protection
- RSA encryption for AES key protection
- User-specific public/private key management
- Gmail sign-in for verified Gmail accounts
- SHA-256 hash-based integrity verification
- Digital signature verification
- Access expiry and access revocation
- Audit logging
- Rule-based suspicious activity detection

## Project Modules

- User registration and login
- Gmail sign-in registration
- RSA key generation
- File upload and AES encryption
- RSA-based AES key encryption
- Secure file download and decryption
- File sharing with selected users
- Access expiry and revocation
- Integrity and digital signature verification
- Audit log management
- Suspicious activity detection
- User and admin dashboard

## Suggested Technology Stack

- Python
- Django
- SQLite or PostgreSQL
- HTML, CSS, Bootstrap, JavaScript
- Python cryptography library
- Google OAuth for Gmail sign-in

## Gmail Sign-In Setup

Add these environment variables before running Gmail sign-in:

- GOOGLE_OAUTH_CLIENT_ID
- GOOGLE_OAUTH_CLIENT_SECRET

Add these callback URLs in Google Cloud OAuth settings:

- http://127.0.0.1:8010/accounts/google/callback/
- https://your-deployed-domain/accounts/google/callback/

## Folder Structure

- Databases
- datasets
- Documentation
- Modules
- PPT
- Source Code
- Test Cases
- UML Diagrams
- Video
