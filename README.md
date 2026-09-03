# LEVELLY

> **Understand your income. Build your safety. Grow when you're ready. Borrow responsibly.**

LEVELLY is an intelligent financial-resilience platform designed for gig and informal workers whose income changes daily or weekly. It combines financial resilience (PS4) with proactive financial-distress prevention (PS3).

---

## 1. Problem Statement

Gig workers and informal workers often have irregular earnings while traditional banking systems are designed around fixed salaries and predictable monthly income.

LEVELLY addresses two related problem statements:

### PS3 — Preventing Financial Distress Before It Becomes a Crisis
How might banks responsibly identify early signs of financial distress and provide personalized interventions that help customers avoid excessive debt, loan defaults, and financial exclusion?

### PS4 — Financial Resilience for Gig and Informal Workers
How might banking technology help gig workers and individuals with irregular incomes build financial resilience through intelligent savings, responsible access to credit, and personalized financial guidance?

### Core Problem

There is no unified solution that continuously understands irregular income, helps workers build financial resilience, detects financial distress early, and responsibly controls additional borrowing before temporary financial pressure becomes excessive debt or default.

---

## 2. Solution Overview

LEVELLY uses **Income Intelligence** as the central engine.

```text
Income / Payments / Expenses
          |
          v
  Income Intelligence
          |
   +------+------+
   |      |      |
   v      v      v
 Save   Distress  Financial
at-Pay  Detection  Resilience
   |      |          |
   v      v          v
Safety  Guardrail  Guidance
Wallet    |
   |       v
   |     Credit
   |       |
   |    Partner
   |      NBFC
   |
   v
Grow / Investments
   |
User Review
   |
Explicit Confirmation
   |
Regulated Partner
```

LEVELLY is an **intelligence and user-experience layer**, not the lender and not an automatic investment engine.

---

## 3. Key Features

### 3.1 Income Intelligence
Continuously analyzes:
- Gig-platform payouts
- Bank transactions
- UPI transactions
- Manual income entries
- Income trends
- Income volatility
- Recent earning pace
- Expense pressure
- Savings behavior

### 3.2 Smart Save-at-Pay
For each payment, LEVELLY suggests a small savings contribution based on the transaction category and current financial condition.

Example:

```text
Food payment = ₹1,000
Suggested saving = 10%
Suggested contribution = ₹100
```

The user chooses:

```text
Pay + Save ₹100
       OR
Pay ₹1,000
```

Savings are **never taken without explicit user consent**.

### 3.3 Category-Based Saving
Example configurable policies:

| Category | Example Suggested Saving |
|---|---:|
| Food | 10% |
| Fuel | 5% |
| Education | 8% |
| Entertainment | 5% |
| Shopping | 10% |
| Family | 5% |
| Healthcare | 5% |
| Other | 5% |

These are configurable product/demo values, not universal financial advice.

### 3.4 Safety Wallet
LEVELLY maintains a protected emergency reserve.

Example:

```text
Safety Wallet = ₹8,200
Safety Target = ₹10,000
Progress = 82%
```

The Safety Wallet is separate from normal spending. The current design intentionally does **not** require a separate Daily Wallet; everyday payments are made through the user's linked bank/UPI payment flow.

### 3.5 LEVELLY Pay
The payment experience is designed around a bank/UPI-linked account.

Flow:

```text
Scan QR / Enter UPI ID
        |
        v
Merchant Details
        |
        v
Enter Amount
        |
        v
Category Detection
        |
        v
Save-at-Pay Suggestion
        |
        v
User Consent
        |
        +----------------+
        |                |
        v                v
 Pay + Save          Pay Only
        |                |
        +-------+--------+
                v
        Payment Completion
```

### 3.6 Large Expense Protection
When a large payment could consume most of the Safety Wallet, LEVELLY shows the user the financial impact before confirmation.

Example:

```text
Requested = ₹8,000
Safety Wallet = ₹8,200
Safety usage ≈ 97.6%
Remaining ≈ ₹200
```

### 3.7 Piggy-Bank Intervention
A premium piggy-bank interaction makes the consequence of spending emergency savings visible.

The intervention:
- Shows current Safety Wallet balance
- Shows requested expense
- Calculates buffer usage
- Animates coins leaving the piggy bank
- Shows remaining emergency savings
- Offers the choice to use savings or explore alternatives

This is a behavioral-finance UX feature, not a hard block.

### 3.8 Responsible Alternative Credit
Credit recommendations consider:
- Income consistency
- Platform tenure
- Savings behavior
- Recent income
- Historical income
- Expense pressure
- Financial resilience
- Distress level

Actual lending is handled by the regulated bank/NBFC partner.

### 3.9 Early Distress Detection
LEVELLY monitors:
- Sustained income decline
- Rising expense-to-income ratio
- Safety Wallet depletion
- Credit pressure
- Declining financial resilience

Distress should be based on sustained changes rather than one unusual day.

### 3.10 Responsible-Lending Guardrail
This is LEVELLY's core differentiator.

```text
Low distress      -> Normal credit recommendation
Moderate distress -> Smaller / capped recommendation
High distress     -> Reduced / held recommendation
Severe distress   -> Hold + financial guidance
```

Preferred UI language:

> **Credit temporarily held**

rather than:

> Loan rejected

The purpose is to protect financial stability rather than maximize loan volume.

### 3.11 Personalized Nudges
Examples:
- "Your recent earnings are below your usual range."
- "Your fuel spending increased 18% this week."
- "You're ₹1,800 away from your Safety Wallet target."
- "Consider delaying a non-essential payment this week."

### 3.12 Financial Resilience Score
LEVELLY can maintain an internal 0–100 resilience score using factors such as:
- Income Stability
- Savings Progress
- Expense Control
- Emergency Readiness
- Credit Pressure

This is **not CIBIL** and must not be represented as an official credit score.

### 3.13 Optional Investment Suggestions
When the Safety Wallet is sufficiently funded and the user's current financial condition is healthy, LEVELLY can present optional investment suggestions.

Possible categories:
- Liquidity-focused savings/deposit products
- Government securities
- Suitable fixed-income products
- Debt-oriented investment products

Important:
- LEVELLY never invests automatically.
- The user chooses an amount.
- The user reviews the product.
- The user explicitly confirms.
- A regulated partner executes the investment.

### 3.14 Investment Pause
If financial distress becomes high, LEVELLY can pause new investment suggestions and prioritize liquidity and emergency savings.

Existing investments should not be automatically sold or altered.

### 3.15 Levelly Coach
A conversational financial-guidance assistant can explain:
- Why saving changed
- Why credit changed
- Why credit was held
- Why investment suggestions paused
- How the Safety Wallet works
- How to reach a savings target

The AI provider is an implementation detail and is not shown in the user interface.

---

## 4. End-to-End User Journey

### Normal payment

```text
Arjun receives payout
       |
       v
Income Intelligence updates profile
       |
       v
Arjun scans a merchant QR
       |
       v
Merchant is resolved
       |
       v
Arjun enters ₹1,000
       |
       v
Category = Food
       |
       v
LEVELLY suggests 10% saving = ₹100
       |
       v
Arjun selects "Pay + Save ₹100"
       |
       +-------> ₹1,000 payment to merchant
       |
       +-------> ₹100 Safety Wallet contribution
       |
       v
Payment success + Safety Wallet update
```

### Large expense

```text
Arjun scans Bike Service QR
       |
       v
Amount = ₹8,000
       |
       v
Safety Wallet = ₹8,200
       |
       v
~97.6% of safety buffer would be consumed
       |
       v
Piggy-bank intervention
       |
       +---------------------+
       |                     |
       v                     v
Use Savings          Explore Partner Credit
```

### Distress

```text
Historical income = ₹24,000
Recent income:
₹21,000 -> ₹18,000 -> ₹15,000
       |
       v
Expense pressure increases
       |
       v
Distress increases
       |
       v
Responsible-Lending Guardrail
       |
       +----------------------+
       |                      |
       v                      v
Credit reduced/held      Guidance shown
       |
       v
Investment suggestions paused
```

---

## 5. System Architecture

```text
                       LEVELLY
                          |
             +------------+------------+
             |                         |
             v                         v
       LEVELLY PAY              FINANCIAL INTELLIGENCE
             |                         |
       UPI / QR / Intent          Income Intelligence
             |                         |
          Merchant                Save-at-Pay
             |                         |
          Amount                 Safety Wallet
             |                         |
             +-------------+-----------+
                           |
                    Financial Profile
                           |
         +-----------------+------------------+
         |                 |                  |
         v                 v                  v
    Distress Engine   Credit Engine     Investment Engine
         |                 |                  |
         v                 v                  v
      Nudges          Guardrail         Suggestions
                           |                  |
                           v                  v
                      Partner NBFC      User Confirmation
                                              |
                                              v
                                       Regulated Partner
```

---

## 6. Recommended Technology Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query or equivalent API-state layer

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

### Database
- PostgreSQL

### AI
- Groq API through the backend only

### Development Integrations
- Mock UPI/payment provider
- Mock NBFC provider
- Mock investment provider

### Production Integration Boundary
Provider adapters should allow replacement of mock services with approved/regulated production providers without rewriting the business logic or UI.

---

## 7. Backend Services

Suggested services:

```text
income_intelligence.py
savings_engine.py
category_service.py
payment_service.py
wallet_service.py
distress_engine.py
credit_engine.py
guardrail.py
investment_engine.py
notification_service.py
coach_service.py
```

Suggested integration modules:

```text
mock_upi.py
mock_nbfc.py
mock_investment_provider.py
groq_client.py
```

---

## 8. Database Models

Core models:

```text
User
LinkedPaymentAccount
Merchant
PaymentTransaction
PaymentProviderEvent
SafetyWallet
Transaction
IncomeTransaction
ExpenseTransaction
SavingsPreference
SavingsTransaction
FinancialProfile
FinancialScoreHistory
DistressEvent
CreditRequest
PartnerCreditOffer
InvestmentProduct
InvestmentSuggestion
InvestmentConsent
InvestmentOrder
Notification
CoachConversation
AuditLog
```

### Key relationship

```text
PaymentTransaction
       |
       +---- Optional SavingsTransaction
```

This maintains traceability between a payment, user consent, and resulting savings contribution.

---

## 9. Important API Endpoints

### Authentication

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

### Income

```http
POST /api/income/transaction
GET  /api/income/summary
GET  /api/income/trend
GET  /api/income/volatility
```

### Payments

```http
POST /api/payments/preview
POST /api/payments/confirm
GET  /api/payments/{id}
POST /api/payments/webhook
```

### Merchant / QR

```http
POST /api/qr/resolve
GET  /api/merchants/{id}
```

### Safety

```http
GET  /api/safety
PUT  /api/safety/target
GET  /api/safety/history
```

### Large expense

```http
POST /api/expenses/large/preview
POST /api/expenses/large/confirm
```

### Financial health

```http
GET /api/financial-health
GET /api/distress
GET /api/nudges
```

### Credit

```http
POST /api/credit/evaluate
GET  /api/credit/profile
GET  /api/credit/offers
POST /api/credit/apply
GET  /api/credit/{id}/status
```

### Investments

```http
GET  /api/investments/suggestions
GET  /api/investments/products/{id}
POST /api/investments/review
POST /api/investments/confirm
GET  /api/investments/{id}/status
```

### Coach

```http
POST /api/coach/message
GET  /api/coach/conversations
```

---

## 10. Payment API Example

### Preview

```json
POST /api/payments/preview

{
  "merchant_id": "M001",
  "amount": 1000
}
```

Example response:

```json
{
  "merchant": "Sri Krishna Supermarket",
  "amount": 1000,
  "category": "food",
  "suggested_percentage": 10,
  "suggested_save_amount": 100,
  "safety_wallet_balance": 8200
}
```

### Confirm

```json
POST /api/payments/confirm

{
  "merchant_id": "M001",
  "amount": 1000,
  "save_consent": true,
  "suggested_save_amount": 100
}
```

The backend must recompute and validate the financial values. Never trust the frontend as the source of truth.

---

## 11. Save-at-Pay Rules

The payment and savings flow must obey:

```text
Payment = user's actual merchant payment

Savings = optional contribution

save_consent = explicit user decision
```

If consent is:

```text
true
```

record the savings contribution.

If consent is:

```text
false
```

complete the payment normally and record no savings contribution.

Use idempotency/transaction controls to avoid duplicate savings during retries.

---

## 12. UPI / Payment Architecture

### Development

Use:

```text
MockUPIPaymentProvider
```

with predefined merchant QR records.

Example:

```text
Merchant: Sri Krishna Supermarket
UPI ID: srikrishna@upi
Category: Food & Grocery
```

### Production

Use an approved payment/UPI integration through the appropriate provider/regulated ecosystem.

The application should abstract payment execution behind:

```text
PaymentProvider
```

Suggested methods:

```text
createPayment()
initiateUPIPayment()
getPaymentStatus()
handleWebhook()
refundPayment()
```

Do not implement UPI network rails directly inside LEVELLY.

Do not request or store:
- UPI PIN
- Bank passwords
- ATM PIN
- Card PIN
- OTP credentials

---

## 13. Environment Variables

Create `.env.example`:

```env
# Application
APP_ENV=development
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173

# Database
DATABASE_URL=postgresql+psycopg://levelly:levelly@localhost:5432/levelly

# Authentication
SECRET_KEY=change-me
JWT_SECRET=change-me

# Groq - backend only
GROQ_API_KEY=
GROQ_MODEL=

# Payment
PAYMENT_PROVIDER=mock
PAYMENT_PROVIDER_API_URL=
PAYMENT_PROVIDER_KEY=
PAYMENT_PROVIDER_SECRET=

# Credit partner
NBFC_PROVIDER=mock
NBFC_API_URL=
NBFC_API_KEY=

# Investment partner
INVESTMENT_PROVIDER=mock
INVESTMENT_API_URL=
INVESTMENT_API_KEY=
```

Never commit `.env`.

Never put server secrets in frontend code.

---

## 14. Docker

Recommended services:

```text
postgres
backend
frontend
```

Use a persistent PostgreSQL Docker volume.

Example:

```bash
docker compose up -d
```

---

## 15. Local Development

### Backend

```bash
cd backend
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
alembic upgrade head
```

Seed data:

```bash
python -m app.seed
```

Start API:

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Expected development URLs:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
API docs: http://localhost:8000/docs
```

Use environment variables for any deployed URLs instead of hard-coding localhost.

---

## 16. Demo Data

Primary user:

```text
Arjun Kumar
Age: 26
Occupation: Food Delivery Rider
Location: Chennai
Platform tenure: 2 years
```

Healthy state:

```text
Average income: ₹24,000
Recent income: ₹24,500
Safety Wallet: ₹10,500
Safety target: ₹10,000
Resilience: 78
Distress: LOW
Credit: AVAILABLE
Grow: AVAILABLE
```

Financial-pressure state:

```text
Average income: ₹24,000
Recent income: ₹15,000
Safety Wallet: ₹8,200
Safety target: ₹10,000
Resilience: 58
Distress: HIGH
Credit: REDUCED / HELD
Grow: PAUSED
```

Example payment:

```text
Merchant: Sri Krishna Supermarket
Category: Food
Amount: ₹1,000
Suggested Save: ₹100
```

Example large expense:

```text
Merchant: BikeCare Service
Category: Vehicle Repair
Amount: ₹8,000
Safety Wallet: ₹8,200
Safety usage: ~97.6%
```

---

## 17. Responsive Design

LEVELLY is mobile-first and should be deployable as a responsive web application.

Required viewport testing:

```text
320px
360px
375px
390px
414px
430px
768px
1024px
1280px
1440px
1920px
```

Requirements:
- No horizontal scrolling
- No clipped cards
- No overflowing charts
- Mobile-friendly QR/payment screens
- Large touch targets
- Responsive bottom navigation
- Responsive modals/bottom sheets
- Safe-area support where appropriate
- Desktop/tablet layouts should adapt rather than simply stretch the mobile layout

---

## 18. Security Principles

- Hash passwords securely.
- Protect authenticated routes.
- Enforce user-level authorization.
- Never expose API secrets to the frontend.
- Never store UPI PINs or bank passwords.
- Validate all API input.
- Use ORM/parameterization.
- Use audit logs for important financial decisions.
- Keep provider integrations server-side.
- Do not trust frontend financial calculations.
- Verify payment status through provider responses/webhooks where applicable.
- Record explicit user consent for savings and investments.

---

## 19. Regulatory/Product Boundaries

LEVELLY is designed as an intelligence layer.

### LEVELLY
- Income analysis
- Financial-health analysis
- Savings recommendation
- Safety Wallet experience
- Distress detection
- Credit recommendation
- Investment suggestion
- User education

### Regulated Credit Partner
- Final lending decision
- Loan terms
- Disbursal
- Repayment servicing

### Investment Partner
- Product execution
- Product documentation
- Transaction processing

For production deployment, appropriate legal, regulatory, payment, lending, investment, privacy and data-consent reviews are required.

---

## 20. Admin Dashboard

Admin can manage configurable product data such as:

- Category saving percentages
- Safety-policy parameters
- Partner offer data
- Investment-product metadata

Admin can view:

- User financial profiles
- Distress states
- Credit recommendations
- Product suggestions

Admin must **not** directly manipulate user consent.

---

## 21. Audit Logging

Audit important events:

```text
Payment confirmation
Save-at-Pay consent
Safety Wallet update
Credit recommendation
Guardrail decision
Credit application
Investment suggestion
Investment consent
Investment execution request
Admin policy change
```

Store:

```text
timestamp
user_id
event_type
action
metadata
```

---

## 22. Testing Requirements

### Backend unit tests
- Average income
- Recent income
- Income trend
- Volatility
- Expense ratio
- Financial resilience
- Save-at-Pay
- Consent
- Wallet updates
- Large expense calculations
- Distress
- Guardrail
- Credit recommendation
- Investment readiness
- Investment consent

### Integration tests
- Payment API
- QR/merchant resolution
- Payment provider
- NBFC provider
- Investment provider
- Database

### Frontend tests
- Payment flow
- Save accepted
- Save declined
- Piggy-bank flow
- Credit reduced/held
- Investment review
- Investment confirmation
- Investment paused

### End-to-end test

```text
Login
→ Scan merchant
→ Enter amount
→ Save suggestion
→ Accept
→ Payment success
→ Safety Wallet update
→ Large expense
→ Piggy-bank
→ Credit alternative
→ Distress
→ Guardrail
→ Grow
→ Investment review
→ Explicit confirmation
→ Status
→ Levelly Coach
```

---

## 23. Frontend Screen Structure

### Onboarding
1. Splash
2. Welcome
3. Occupation
4. Income frequency
5. Connect income
6. Safety target
7. Two-wallet introduction

### Home
8. Home healthy
9. Home financial-pressure state
10. Income Intelligence
11. Income history
12. Financial Resilience

### Payments
13. LEVELLY Pay
14. QR Scanner
15. Merchant Details
16. Payment Category
17. Payment Amount
18. Save-at-Pay
19. Save Explanation
20. Payment Review
21. Payment Success

### Safety
22. Safety Wallet
23. Safety Target
24. Large Expense
25. Savings Impact
26. Piggy-Bank Intervention

### Credit
27. Credit Overview
28. Partner NBFC
29. Credit Offer
30. Distress Detection
31. Responsible-Lending Guardrail
32. Personalized Nudges

### Grow
33. Grow Overview
34. Investment Suggestions
35. Investment Details
36. Investment Amount
37. Investment Review
38. Investment Confirmation
39. Investment Status
40. Investment Paused

### Analytics / Account
41. Transactions
42. Expense Analytics
43. Notifications
44. Levelly Coach
45. Profile
46. Linked Bank & UPI
47. Save Preferences
48. Privacy & Consent

---

## 24. Important User Experience Rules

### Payment
Never hide the savings contribution.

Show:

```text
Merchant payment: ₹1,000
Optional Safety Save: ₹100
Total cash impact: ₹1,100
```

### Investment
Never imply automatic investment.

Show:

```text
Suggestion
→ Review
→ Choose
→ Confirm
→ Partner executes
```

### Credit
Never aggressively push borrowing.

Show:

```text
Current financial position
+
Recommended amount
+
Reason
```

### Distress
Never shame the user.

Prefer:

> "Let's protect your financial buffer first."

### Savings
Declining a Save-at-Pay suggestion must not block a payment.

---

## 25. Future Scope

Possible future capabilities:

- Multi-platform income aggregation
- Income forecasting
- Seasonality detection
- Advanced anomaly detection
- More sophisticated savings policies
- Financial recovery planning
- Emergency-fund recommendations
- Financial goals
- What-if financial scenarios
- Insurance/protection recommendations
- Multilingual Levelly Coach
- Production UPI/payment integration
- Real partner-bank/NBFC integration
- Real investment-provider integration

---

## 26. Suggested Future Advanced Features

### Financial Recovery Planner

After a large Safety Wallet withdrawal:

```text
Current reserve: ₹200
Target: ₹10,000
Gap: ₹9,800
Suggested rebuild pace: configurable
Estimated recovery period: based on actual accepted savings
```

### What-If Engine

Example:

> "What happens if my income falls by 20%?"

LEVELLY can show projected effects on:
- Expense pressure
- Safety target
- Saving suggestions
- Credit recommendation
- Investment readiness

### Income Forecast

Show an estimated upcoming income range based on available historical data, clearly labeled as an estimate.

---

## 27. Folder Structure

Recommended:

```text
levelly/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── api/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   └── .env.example
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── engines/
│   │   ├── integrations/
│   │   └── tests/
│   ├── alembic/
│   ├── requirements.txt
│   └── .env.example
│
├── database/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 28. Demo Narrative

The strongest demo should tell one continuous story.

### Step 1
Arjun receives an income payout.

### Step 2
LEVELLY updates his financial profile.

### Step 3
Arjun scans a merchant QR.

### Step 4
LEVELLY identifies the merchant and category.

### Step 5
Arjun enters ₹1,000.

### Step 6
LEVELLY suggests:

```text
Save 10% = ₹100
```

### Step 7
Arjun chooses:

```text
Pay + Save ₹100
```

### Step 8
Payment completes and Safety Wallet increases.

### Step 9
Arjun later needs ₹8,000 for a bike repair.

### Step 10
LEVELLY calculates:

```text
97.6% of Safety Wallet would be consumed.
```

### Step 11
Piggy-bank intervention appears.

### Step 12
Arjun explores partner credit.

### Step 13
LEVELLY checks current distress.

### Step 14
If financial pressure is high:

```text
Credit recommendation reduced / held
Investment suggestions paused
Personalized guidance shown
```

### Step 15
When Arjun's finances recover and the Safety Wallet is healthy:

```text
Optional investment suggestions become available.
```

### Step 16
Arjun reviews and explicitly confirms an investment.

### Step 17
The regulated partner handles execution.

---

## 29. Core Differentiator

Most financial products ask:

> **"Can this person borrow?"**

LEVELLY also asks:

> **"Is this a safe time for this person to borrow?"**

This is the connection between PS4 and PS3.

```text
PS4:
Build financial resilience

        +

PS3:
Prevent financial distress

        =

LEVELLY
```

---

## 30. Final Pitch

> **LEVELLY is an intelligent financial-resilience platform for gig workers that continuously understands irregular income, lets users build emergency savings one transaction at a time, protects them from draining that buffer, detects financial distress before it becomes a crisis, provides responsible access to partner credit, and suggests investments only when they are financially ready.**

### One-line USP

> **"LEVELLY doesn't just help you borrow. It helps you know when you shouldn't."**

---

## 31. Deployment

The frontend should be deployable separately from the backend.

### Frontend

Recommended:
- Vercel
- Netlify
- Cloudflare Pages

Use:

```env
VITE_API_URL=
```

Never hard-code backend URLs.

### Backend

Can be deployed to a cloud/container platform that supports FastAPI.

Configure:

```env
DATABASE_URL=
FRONTEND_URL=
CORS_ORIGINS=
GROQ_API_KEY=
PAYMENT_PROVIDER=
NBFC_PROVIDER=
INVESTMENT_PROVIDER=
```

### Production architecture

```text
User Mobile Browser
        |
        v
LEVELLY Responsive Frontend
        |
       HTTPS
        |
        v
LEVELLY FastAPI Backend
   +----+----+----+
   |    |    |    |
   v    v    v    v
Postgres Groq Payment Partners
```

---

## 32. Project Status Model

For development, keep these providers configurable:

```text
PAYMENT_PROVIDER=mock
NBFC_PROVIDER=mock
INVESTMENT_PROVIDER=mock
```

Later replace them with approved production integrations.

The business logic and frontend should remain unchanged.

---

## 33. Final Architecture Principle

```text
BANK / UPI
   ↓
LEVELLY PAY
   ↓
FINANCIAL INTELLIGENCE
   ↓
SAVE / PROTECT / DISTRESS / CREDIT / GROW
   ↓
USER DECISION
   ↓
REGULATED PARTNER
```

LEVELLY's value is the **intelligence, personalization, transparency, and responsible intervention layer** connecting everyday financial activity with long-term financial resilience.

---

## 34. License / Usage

This README describes the LEVELLY hackathon/project prototype architecture. Before production use, verify all applicable legal, regulatory, payment, lending, investment, privacy and data-protection requirements with appropriate professional and regulated partners.

---

**LEVELLY**

*Understand your income. Build your safety. Grow when you're ready. Borrow responsibly.*
