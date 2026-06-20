# Two-Factor Authentication (2FA) Setup Guide
**NexaCloud Support | Article ID: ACC-005 | Last Updated: 2025-06-01**

---

## Overview

Two-Factor Authentication (2FA) adds a second layer of security to your NexaCloud account. Even if your password is compromised, 2FA prevents unauthorized access. This guide covers setup, management, and troubleshooting for 2FA.

---

## 1. Why Enable 2FA?

- **Protects against password breaches:** Even with your password, attackers cannot log in without the second factor
- **Required for compliance:** Some organizations require 2FA for SOC2 and ISO 27001 compliance
- **Organizational enforcement:** Admins can mandate 2FA for all team members

---

## 2. Supported 2FA Methods

| Method | Security Level | Recommended |
|---|---|---|
| **Authenticator App (TOTP)** | High | ✅ Recommended |
| **SMS (Text Message)** | Medium | Available |
| **Hardware Security Key (FIDO2)** | Very High | Enterprise recommended |
| **Email OTP** | Low | Backup only |

---

## 3. Setting Up Authenticator App (TOTP)

### Compatible Authenticator Apps
- Google Authenticator (iOS/Android)
- Authy (iOS/Android/Desktop)
- Microsoft Authenticator (iOS/Android)
- 1Password
- Bitwarden (Premium)

### Setup Steps
1. Install an authenticator app on your mobile device
2. Log in to NexaCloud and go to **Settings → Security → Two-Factor Authentication**
3. Click **"Enable 2FA"**
4. Choose **"Authenticator App"**
5. A QR code will appear on screen
6. Open your authenticator app and tap **"+"** or **"Add Account"**
7. Scan the QR code with your phone's camera
8. Your authenticator app will now show a 6-digit code that refreshes every 30 seconds
9. Enter the current 6-digit code in NexaCloud to verify setup
10. Click **"Enable"**
11. **Save your backup codes** — you will see 8 one-time backup codes. Store them securely.

> ⚠️ **Critical:** If you lose access to your authenticator app AND your backup codes, you may lose access to your account permanently. Store backup codes in a password manager or secure physical location.

---

## 4. Setting Up SMS 2FA

> **Note:** SMS 2FA is less secure than authenticator apps due to SIM-swapping attacks. We recommend authenticator apps.

### Setup Steps
1. Go to **Settings → Security → Two-Factor Authentication**
2. Click **"Enable 2FA"**
3. Choose **"SMS"**
4. Enter your mobile phone number with country code (e.g., +91-9876543210)
5. Click **"Send Verification Code"**
6. Enter the 6-digit code received via SMS
7. Click **"Verify & Enable"**

### SMS Not Received?
- Wait up to 2 minutes
- Click **"Resend Code"** (previous code is invalidated)
- Check your phone's signal strength
- Verify the phone number is correct
- Some carriers block automated SMS — switch to authenticator app

---

## 5. Setting Up Hardware Security Key (FIDO2/WebAuthn)

*Available on Business and Enterprise plans.*

### Compatible Hardware Keys
- YubiKey 5 series
- Google Titan Security Key
- Thetis FIDO2 Key
- Any FIDO2/WebAuthn certified key

### Setup Steps
1. Go to **Settings → Security → Two-Factor Authentication**
2. Click **"Add Security Key"**
3. Plug your security key into a USB port (or hold near phone for NFC keys)
4. Click **"Register Key"** and follow browser prompts
5. Touch or press the button on your security key when prompted
6. Give your key a name (e.g., "YubiKey - Office")
7. Click **"Save"**

You can register up to 5 hardware keys per account.

---

## 6. Backup Codes

### What Are Backup Codes?
Backup codes are one-time-use codes that allow you to log in if you lose access to your 2FA device. Each NexaCloud account has 8 backup codes.

### Viewing and Regenerating Backup Codes
1. Go to **Settings → Security → Two-Factor Authentication**
2. Click **"View Backup Codes"**
3. Re-authenticate to confirm identity
4. Copy and store codes securely
5. To generate new codes: Click **"Regenerate Codes"** (old codes become invalid)

### Using a Backup Code to Log In
1. On the 2FA prompt page, click **"Use a backup code"**
2. Enter one of your 8-digit backup codes
3. Click **"Verify"**
4. Once logged in, set up a new 2FA method or generate new backup codes immediately

---

## 7. Disabling 2FA

> ⚠️ **Warning:** Disabling 2FA reduces your account security. Only do this if necessary.

### Disabling for Your Account
1. Go to **Settings → Security → Two-Factor Authentication**
2. Click **"Disable 2FA"**
3. Enter your password and a 2FA code to confirm
4. Click **"Disable"**

> **Note:** If your organization has enforced mandatory 2FA, you cannot disable it on your account.

### Admin: Disabling 2FA for a User (if locked out)
1. Go to **Settings → Users & Permissions**
2. Click on the user's account
3. Click **"Reset 2FA"** — this removes their 2FA configuration
4. Notify the user to re-enable 2FA upon next login

---

## 8. Organizational 2FA Policy

### Requiring 2FA for All Members
1. Go to **Settings → Security → Security Policy**
2. Toggle **"Require 2FA for all organization members"** to ON
3. Existing members have **7 days** to enable 2FA before their access is restricted
4. New members must set up 2FA before accessing organization resources

### Monitoring 2FA Compliance
- **Settings → Users & Permissions** shows each user's 2FA status
- Users without 2FA are highlighted
- Admins can send a reminder email to non-compliant users

---

## 9. Troubleshooting

### "Invalid code" even with correct code
- **Time sync issue:** Authenticator apps use time-based codes. Ensure your phone's time is synced automatically (Settings → General → Date & Time → Set Automatically on iOS)
- **Wrong account:** If you have multiple accounts, ensure you're using the correct 2FA entry

### Lost access to 2FA device
1. Use a backup code to log in
2. Go to Settings → Security → Two-Factor Authentication
3. Disable old 2FA and set up a new device

### Locked out with no backup codes
Contact support@nexacloud.io from your registered account email with:
- Government-issued ID (for identity verification)
- Organization name
- Recovery will take 24–48 hours for security verification

---

*Related articles: Password Reset Guide (ACC-001), Data Security Policy (SEC-001), Account Management (ACC-002)*
