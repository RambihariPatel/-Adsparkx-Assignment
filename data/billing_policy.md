# Billing Policy & Payment FAQs
**NexaCloud Support | Article ID: BIL-001 | Last Updated: 2025-06-01**

---

## Overview

This document covers NexaCloud's billing cycles, payment methods, invoice management, failed payments, and refund policy. For plan pricing and feature comparison, see the Subscription Plans guide (BIL-002).

---

## 1. Billing Cycles

### Monthly Billing
- Billed on the same date each month as your initial subscription
- Example: Subscribed on March 15 → billed on the 15th of every month
- Prorated charges apply when upgrading mid-cycle

### Annual Billing
- Billed once per year in advance
- Annual plans receive a **20% discount** compared to monthly pricing
- No prorated refunds for unused months when downgrading

### Billing Date
- Your billing date is displayed in **Settings → Billing → Billing Overview**
- If your billing date falls on a day that doesn't exist in a given month (e.g., March 31 → billed on March 30 in April)

---

## 2. Accepted Payment Methods

| Method | Availability |
|---|---|
| Visa / Mastercard / Amex | All plans |
| UPI (India) | Starter & Professional |
| Net Banking (India) | Starter & Professional |
| Bank Transfer / Wire | Enterprise plans only |
| PayPal | Not currently supported |
| Cryptocurrency | Not supported |

### Adding a Payment Method
1. Go to **Settings → Billing → Payment Methods**
2. Click **"Add Payment Method"**
3. Enter card details — we use Stripe for secure processing
4. Click **"Save"** — this becomes your default payment method

### Updating Payment Method
1. Go to **Settings → Billing → Payment Methods**
2. Click **"Edit"** next to the existing card
3. Update the details and save
4. Alternatively, delete the old method and add a new one

---

## 3. Invoices & Receipts

### Downloading Invoices
1. Go to **Settings → Billing → Invoice History**
2. Find the billing period you need
3. Click **"Download PDF"** or **"Download CSV"**

### Invoice Details Included
- Invoice number and date
- NexaCloud entity details (for GST/VAT compliance)
- Line items by plan and usage
- Tax breakdown (GST for India, VAT for EU)
- Payment method used

### GST / Tax Information
- Indian customers are charged **18% GST** (CGST 9% + SGST 9%)
- Your GSTIN can be added under **Settings → Billing → Tax Information**
- B2B customers in the EU can add their VAT number for reverse-charge

### Sending Invoices to Finance Teams
- Set a separate billing email at **Settings → Billing → Billing Email**
- Multiple CC addresses are supported (comma-separated)

---

## 4. Failed Payments

### What Happens When a Payment Fails
1. **Day 0:** Payment attempted — fails due to insufficient funds, expired card, or bank decline
2. **Day 1:** Email notification sent to account owner and billing email
3. **Day 3:** Second payment retry
4. **Day 7:** Third payment retry + account downgraded to read-only mode
5. **Day 14:** Fourth and final retry
6. **Day 21:** Account suspended — data retained for 30 days

### Resolving a Failed Payment
1. Update your payment method in **Settings → Billing → Payment Methods**
2. Once updated, go to **Settings → Billing → Invoice History**
3. Click **"Retry Payment"** on the outstanding invoice
4. Account is restored immediately upon successful payment

### Common Reasons for Payment Failure
- Expired credit card
- Insufficient funds
- Bank blocking international/online transactions
- Card limit exceeded
- 3D Secure authentication not completed

---

## 5. Upgrades & Downgrades

### Upgrading Your Plan
- Takes effect immediately
- Charged the prorated difference for the remainder of the billing cycle
- All features of the new plan become available instantly

### Downgrading Your Plan
- Monthly: Takes effect at the end of the current billing cycle
- Annual: Takes effect at renewal date
- Features from the higher plan remain available until the change takes effect

---

## 6. Cancellation

### How to Cancel
1. Go to **Settings → Billing → Subscription**
2. Click **"Cancel Subscription"**
3. Select a reason (optional — helps us improve)
4. Confirm cancellation

### What Happens After Cancellation
- Access continues until the end of the paid period
- Data is retained for **60 days** post-cancellation
- After 60 days, all data is permanently deleted
- Reactivating within 60 days restores your data

### Cancelling Mid-Cycle (Monthly Plan)
- No refund for the remainder of the current month
- Access continues until the billing period ends

---

## 7. Refund Policy

See the complete Refund Policy document (BIL-003) for details.

**Summary:**
- 14-day money-back guarantee for new subscriptions
- No refunds for annual plans after 30 days
- Partial refunds at NexaCloud's discretion for service outages

---

## 8. Contact Billing Support

- **Email:** billing@nexacloud.io
- **Live Chat:** Available in-app for Professional and Enterprise plans
- **Response Time:** 1 business day for billing queries

*Related articles: Subscription Plans (BIL-002), Refund Policy (BIL-003), Account Management (ACC-002)*
