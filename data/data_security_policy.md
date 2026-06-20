# Data Security & Privacy Policy
**NexaCloud Support | Article ID: SEC-001 | Last Updated: 2025-06-01**

---

## Overview

NexaCloud is committed to the highest standards of data security and privacy. This document describes how we protect your data, our compliance certifications, and your rights as a data subject.

---

## 1. Security Certifications & Compliance

| Standard | Status |
|---|---|
| SOC 2 Type II | Certified — Report available on request |
| ISO 27001 | Certified |
| GDPR | Compliant |
| CCPA | Compliant |
| HIPAA | Available on Enterprise plan (with BAA) |
| PCI DSS | Level 1 (for payment processing via Stripe) |

### Requesting Compliance Documents
Enterprise customers can request:
- SOC 2 Type II report
- ISO 27001 certificate
- GDPR Data Processing Agreement (DPA)
- HIPAA Business Associate Agreement (BAA)
- Security questionnaire responses

Contact: security@nexacloud.io

---

## 2. Data Encryption

### Data in Transit
- All data transmitted between your browser/app and NexaCloud is encrypted using **TLS 1.3**
- API connections require TLS 1.2 minimum
- HTTP connections are automatically redirected to HTTPS

### Data at Rest
- All data stored in NexaCloud databases is encrypted using **AES-256**
- Encryption keys are managed using AWS KMS (Key Management Service)
- Customer data is logically isolated per organization

### Database Credentials
- All database passwords are stored using bcrypt hashing
- API keys are stored as hashed values and cannot be retrieved after creation

---

## 3. Data Storage & Residency

### Default Storage Regions
| Region | Data Centers |
|---|---|
| Global (default) | US East (primary), EU West (replica) |
| India | Mumbai (ap-south-1) |
| Europe | Frankfurt (eu-central-1) |
| APAC | Singapore (ap-southeast-1) |

### Data Residency (Enterprise)
Enterprise customers can specify data residency to keep all data within a geographic region. Contact your Customer Success Manager to configure.

### Subprocessors
NexaCloud uses the following key subprocessors:
- **AWS** — Cloud infrastructure and storage
- **Stripe** — Payment processing
- **Google** — Analytics and machine learning services
- **Datadog** — Infrastructure monitoring
- **Sendgrid** — Transactional email

Full subprocessor list: [nexacloud.io/subprocessors](https://nexacloud.io/subprocessors)

---

## 4. Access Controls

### Principle of Least Privilege
- NexaCloud employees access customer data only when required for support purposes
- All access requires approval and is logged in an internal audit system
- Production database access requires two-factor authentication and VPN

### NexaCloud Employee Access Policy
- Only authorized personnel can access customer data
- Access is limited to what is necessary to provide the service
- All access is logged and reviewed monthly
- Employees sign NDAs and security policies

### Customer-Controlled Access
- Role-based access control (RBAC) is available on all plans
- Custom roles available on Business and Enterprise plans
- Audit logs of all access events available on Business and Enterprise plans

---

## 5. Network Security

### Infrastructure
- Hosted on AWS with multi-AZ (Availability Zone) redundancy
- Web Application Firewall (WAF) protects against common attacks (SQL injection, XSS, CSRF)
- DDoS protection via AWS Shield

### Penetration Testing
- Annual third-party penetration tests conducted
- Bug bounty program: report vulnerabilities at security@nexacloud.io

### Security Incident Response
1. Detection and classification (within 1 hour)
2. Containment and eradication
3. Customer notification (within 72 hours for material breaches, per GDPR)
4. Post-incident report (within 2 weeks)

---

## 6. GDPR Compliance

### Data Subject Rights
As a data subject under GDPR, you have the right to:
- **Access:** Request a copy of your personal data
- **Rectification:** Correct inaccurate data
- **Erasure:** Request deletion of your personal data ("right to be forgotten")
- **Portability:** Export your data in machine-readable format
- **Restriction:** Limit processing of your data
- **Objection:** Object to specific processing activities

### Exercising Your Rights
Submit a request to: privacy@nexacloud.io
Response time: Within 30 days

### Data Retention
| Data Type | Retention |
|---|---|
| Account data | Until account deletion |
| Usage logs | 1 year |
| Support tickets | 3 years |
| Financial records | 7 years (legal requirement) |
| Marketing emails | Until unsubscribe |

---

## 7. Responsible Disclosure

If you discover a security vulnerability:
1. Email security@nexacloud.io with details
2. Do not publicly disclose until we've had time to remediate
3. We aim to respond within 48 hours and remediate within 90 days
4. Security researchers who responsibly disclose are acknowledged in our Hall of Fame

---

## 8. Your Responsibilities

To keep your NexaCloud account secure:
- Enable MFA on all user accounts
- Use strong, unique passwords
- Rotate API keys regularly
- Restrict API key scopes to minimum required permissions
- Review audit logs for unexpected activity
- Report suspicious activity immediately to security@nexacloud.io
- Keep browser and operating system up to date
- Do not share login credentials

---

*Related articles: Account Management (ACC-002), Two-Factor Authentication (ACC-005), Account Audit Logs (ACC-006)*
