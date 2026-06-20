# Password Reset & Account Recovery Guide
**NexaCloud Support | Article ID: ACC-001 | Last Updated: 2025-06-01**

---

## Overview

This guide covers all methods for resetting your NexaCloud password, recovering a locked account, and troubleshooting Multi-Factor Authentication (MFA) issues. If you are unable to log in, follow the steps below based on your situation.

---

## 1. Standard Password Reset

### Steps to Reset Your Password

1. Navigate to [app.nexacloud.io/login](https://app.nexacloud.io/login)
2. Click **"Forgot Password?"** below the login form
3. Enter the email address associated with your NexaCloud account
4. Click **"Send Reset Link"**
5. Check your inbox for an email from `no-reply@nexacloud.io` (check Spam/Junk if not received within 5 minutes)
6. Click the reset link in the email — it is valid for **30 minutes**
7. Enter and confirm your new password
8. Click **"Reset Password"**
9. Log in with your new credentials

### Password Requirements
- Minimum 12 characters
- At least one uppercase letter (A–Z)
- At least one lowercase letter (a–z)
- At least one number (0–9)
- At least one special character (!@#$%^&*)
- Cannot be the same as the last 5 passwords

---

## 2. Account Locked Due to Failed Login Attempts

Your account is automatically locked after **5 consecutive failed login attempts** as a security measure.

### Automatic Unlock
- The account auto-unlocks after **30 minutes** from the first failed attempt

### Manual Unlock via Password Reset
1. Go to the login page
2. Click **"Forgot Password?"**
3. Complete the standard password reset process
4. This will also unlock your account immediately

### Admin-Assisted Unlock
If you are an Organization Admin:
1. Log in with admin credentials
2. Navigate to **Settings → Users & Permissions**
3. Find the locked user account
4. Click **"Unlock Account"** and optionally force a password reset

---

## 3. Multi-Factor Authentication (MFA) Issues

### Lost Access to Authenticator App

If you have lost access to your MFA device:

1. On the login page, after entering your password, click **"Having trouble with MFA?"**
2. Choose **"Use backup codes"**
3. Enter one of your 8-digit backup codes
4. Once logged in, go to **Settings → Security → MFA** to reconfigure

> **Important:** Each backup code can only be used once.

### MFA Not Received (SMS)
- Wait up to 2 minutes for the SMS to arrive
- Click **"Resend Code"** — this invalidates the previous code
- Verify your phone number is correct in **Settings → Profile**
- Check if your carrier blocks automated SMS

### Reconfiguring MFA After Device Change
1. Log in using a backup code
2. Navigate to **Settings → Security → Multi-Factor Authentication**
3. Click **"Remove current MFA device"**
4. Scan the new QR code with your authenticator app
5. Enter the 6-digit code to confirm setup

---

## 4. Single Sign-On (SSO) Users

If your organization uses SSO (Google Workspace, Okta, Azure AD):
- **You cannot reset your NexaCloud password directly**
- Contact your IT administrator to reset your identity provider password
- After resetting, your NexaCloud access is restored automatically

---

## 5. Common Error Messages

| Error | Meaning | Solution |
|---|---|---|
| "Reset link expired" | Link is older than 30 min | Request a new reset link |
| "Invalid or used link" | Link was already used | Request a new reset link |
| "Account not found" | Email not registered | Check email spelling or contact support |
| "Too many requests" | Rate limit hit | Wait 15 minutes, then retry |
| "MFA code invalid" | Wrong code / time sync issue | Check device clock accuracy |

---

## 6. Still Unable to Access Your Account?

If none of the above steps resolve your issue:

1. Contact **NexaCloud Support** via live chat at [support.nexacloud.io](https://support.nexacloud.io)
2. Email `support@nexacloud.io` with:
   - Your account email
   - Organization name
   - Description of the issue
   - Screenshot of any error messages
3. For enterprise accounts, call your dedicated Customer Success Manager

**Support hours:** Monday–Friday, 9 AM – 6 PM IST | 24/7 for Enterprise plans

---

*Related articles: Two-Factor Authentication Setup (ACC-005), Account Management (ACC-002), SSO Configuration (INT-003)*
