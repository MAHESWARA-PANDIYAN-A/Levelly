# LEVELLY 🛡️

> **"Understand your income. Build your safety. Grow when you're ready. Borrow responsibly."**

LEVELLY is an end-to-end fintech platform tailored for gig economy workers, freelancers, and variable-income earners in India. By bridging income volatility intelligence with behavioral nudges, dual-wallet mechanics, automated micro-savings, safety-gated investing, and responsible-lending guardrails, LEVELLY ensures users never fall into predatory debt spirals.

---

## 🌟 Key Product Pillars

### 1. Income Intelligence Engine
- **Rolling Volatility Analysis:** Computes the coefficient of variation ($CV = \sigma / \mu$) across historical payouts.
- **Decline & Trend Detection:** Compares recent earning velocity (rolling 14-day pace) against the 90-day baseline to detect income dips before emergency borrowing occurs.
- **Sustained Distress vs Bad Day:** Analyzes consecutive below-baseline weekly periods so temporary dips don't trigger unwarranted panics.

### 2. Two-Wallet Architecture
- **Daily Wallet:** For immediate operational expenses, groceries, fuel, and bill payments.
- **Safety Wallet (Piggy Bank):** Dedicated liquid emergency reserve with progress tracking toward a dynamic target (default ₹10,000).
- **Surplus Trigger:** Funds above the 100% safety target unlock micro-investment recommendations.

### 3. Smart Save-at-Pay
- Micro-savings seamlessly attached to regular everyday payments.
- **Dynamic Distress Scaling:** When financial distress is detected (e.g. HIGH distress), the suggested savings percentage automatically dampens (e.g., reduces by 75% down to 2.5%) to relieve cash flow pressure.
- **Full User Agency:** Users can toggle, adjust, or decline savings at any checkout with a single tap.

### 4. Piggy Bank Wobble (Large Expense Analysis)
- Pre-purchase impact simulator that visualizes how an upcoming large expense will shake or deplete the emergency safety reserve.
- Delivers concrete recovery estimates (e.g. "Will take ~4 weeks to replenish at current pace").

### 5. Responsible-Lending Guardrail
- **Held & Reduced (Never "Rejected"):** Uses positive, dignity-preserving language. Credit requests under distress are held with a clear explanation and recovery roadmap, protecting the user from debt-traps.
- **Platform Tenure Boost:** Positive earning discipline on the platform progressively expands credit capacity.
- **NBFC Partner Abstraction:** Decoupled adapter layer isolating partner credit disbursement APIs. Held loans are intercepted before reaching third-party lenders.

### 6. Safety-Gated Investment System
- **Gated by Safety Buffer:** Investment products (Liquid Mutual Funds, Digital Gold) are locked until the Safety Wallet target (100%) is achieved.
- **Explicit Informed Consent:** Enforces statutory risk disclosures, lock-in duration terms, and complete compliance audit logging before any order is placed.

### 7. Levelly Coach (AI Financial Companion)
- Powered by **Groq LLaMA 3.1-8b-instant** LLM.
- Injects live financial telemetry (distress level, wallet balances, income decline percentage, active loan holds) directly into the system prompt for contextual, non-judgmental guidance.

---

## 🛠️ Architecture & Tech Stack

```
                                  LEVELLY ARCHITECTURE
                                  
  ┌────────────────────────────────────────────────────────────────────────┐
  │                           React + TypeScript                           │
  │                  Tailwind CSS • Lucide Icons • Recharts                │
  │                     TanStack Query • Zustand Store                     │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │ REST APIs / JWT
  ┌───────────────────────────────────▼────────────────────────────────────┐
  │                            FastAPI Backend                             │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │                        Core Engine Layer                         │  │
  │  │  • Income Intelligence     • Distress Detection (4-tier)         │  │
  │  │  • Expense & Nudges        • Responsible-Lending Guardrails      │  │
  │  │  • Save-at-Pay Dynamic     • Safety-Gated Investments            │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │                       Integration Layer                          │  │
  │  │  • Groq LLaMA 3.1 Coach   • Partner NBFC Adapter (Mock)          │  │
  │  │  • Audit Trail Logger     • In-App Notification Dispatcher       │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  └───────────────────────────────────┬────────────────────────────────────┘
                                      │ SQLAlchemy 2.0
  ┌───────────────────────────────────▼────────────────────────────────────┐
  │                          PostgreSQL Database                           │
  │      21 Normalized Tables: Wallets, Transactions, Policies,            │
  │      Distress Events, Consents, Credit Requests, Audit Logs            │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart (Local Run)

### Option 1: One-Click Windows Script (Recommended)

From the project root:

```powershell
.\start.ps1
```

This PowerShell script automatically:
1. Verifies PostgreSQL connectivity.
2. Creates and activates the Python virtual environment (`levelly/backend/venv`).
3. Installs backend dependencies (`pip install -r requirements.txt`).
4. Executes schema creation & applies migrations.
5. Seeds the database with demo users, 90-day transaction history, and distress signals.
6. Installs frontend npm packages (if needed) and spins up Vite.
7. Concurrently launches the FastAPI backend and React frontend.

---

### Option 2: Manual Step-by-Step Setup

#### 1. Configure Environment
```bash
cd levelly
cp .env.example .env
# Edit DATABASE_URL or GROQ_API_KEY in .env if needed
```

#### 2. Backend Setup
```bash
cd levelly/backend
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
python -c "from app.core.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine)"
python app/seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Frontend Setup
```bash
cd levelly/frontend
npm install
npm run dev
```

---

## 👤 Seed Data & Demo Accounts

The database comes pre-seeded with complete, realistic gig-worker financial profiles:

### Primary Persona: Arjun Kumar (State B - Financial Pressure)
- **Email:** `arjun@levelly.app`
- **Password:** `Levelly@123`
- **Role:** Delivery & rideshare gig partner (3 years tenure)
- **Profile Scenario:**
  - Historical average income: **₹24,000 / month**
  - Recent earnings velocity: **₹15,000 / month** (37.5% decline)
  - Distress Level: **HIGH**
  - Resilience Score: **58 / 100**
  - Safety Wallet Balance: **₹8,200 / ₹10,000** (82% funded)
  - Behavioral response: Save-at-Pay recommendation automatically dampens from 10% to 2.5%; investment unlock is held until Safety reaches 100%; loan requests trigger protective guardrails with positive recovery recommendations.

### Administrator Account
- **Email:** `admin@levelly.app`
- **Password:** `Admin@Levelly123`
- **Role:** System Administrator

---

## 🧪 Running the Test Suite

The automated test suite verifies all mathematical models, guardrail policies, and state transitions using `pytest`:

```bash
cd levelly/backend
.\venv\Scripts\pytest app\tests\test_levelly.py -v
```

### Coverage Highlights (34 passing tests):
- `TestIncomeIntelligence`: Volatility calculations, trend direction, consecutive low periods.
- `TestExpenseEngine`: Essential vs non-essential ratio and dynamic expense nudges.
- `TestDistressEngine`: 4-tier classification (LOW, MODERATE, HIGH, SEVERE).
- `TestGuardrail`: Responsible-lending hold rules, verification of dignity-preserving non-rejection phrasing.
- `TestCreditEngine`: NBFC offer filtering, platform tenure boosts, held credit interception.
- `TestInvestmentEngine`: Safety Wallet target gating, pause triggers during distress.
- `TestWalletLogic`: Dual-wallet balances, surplus routing, Piggy Bank wobble impact calculations.
- `TestEndToEnd`: Save-at-Pay transaction flows, explicit consent audit trail creation.

---

## 📚 API Endpoints Overview

| Category | Method | Endpoint | Description |
|---|---|---|---|
| **Auth** | `POST` | `/api/auth/login` | OAuth2 password flow, returns JWT access token |
| | `POST` | `/api/auth/register` | Create user and provision Daily & Safety wallets |
| **Health** | `GET` | `/api/financial-health/dashboard` | Aggregated dashboard, distress level, resilience score |
| | `GET` | `/api/financial-health/distress-signals` | Active distress indicators |
| **Wallets** | `GET` | `/api/wallets` | Balances, safety progress percentage, surplus amount |
| | `POST` | `/api/wallets/large-expense-preview` | Piggy Bank wobble & recovery timeframe simulation |
| **Payments** | `POST` | `/api/payments/preview` | Dynamic Save-at-Pay suggestion with distress dampening |
| | `POST` | `/api/payments/confirm` | Execute payment + optional micro-saving split |
| **Credit** | `POST` | `/api/credit/recommendation` | Evaluates eligibility through responsible guardrails |
| | `POST` | `/api/credit/request` | Submits loan application to NBFC adapter (or holds) |
| **Invest** | `GET` | `/api/investments/suggestions` | Safety-gated product list |
| | `POST` | `/api/investments/consent` | Records mandatory explicit consent & statutory audit |
| **Coach** | `POST` | `/api/coach/message` | AI conversation enriched with live user financial state |
| **Nudges** | `GET` | `/api/nudges` | Actionable behavioral prompts based on recent activity |

---

## 🔒 Security & Compliance
- **Password Hashing:** Passlib with Bcrypt.
- **Statutory Audit Trails:** Every credit evaluation and investment consent logs an immutable `audit_logs` entry with timestamp, actor, and terms version.
- **Non-Predatory Guarantee:** No user in severe distress is offered high-interest partner credit products.

---

## 📄 License
This project is licensed under the MIT License.
