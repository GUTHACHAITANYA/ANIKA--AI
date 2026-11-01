# ANIKA-AI
### AI-Powered OCR Expense Splitting & Financial Intelligence Platform

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![React 18](https://img.shields.io/badge/react-18.3-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/typescript-5.7-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/vite-6.2-646CFF.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/tests-29%20passed-brightgreen.svg)]()

---

## 1. Project Overview

**ANIKA-AI** is an intelligent, full-stack financial intelligence and expense management platform designed to automate the entire lifecycle of shared spending. Users can upload single or batch receipts, invoices, and PDFs to extract structured financial data, classify expense categories via a trained machine learning model, assign participants, choose among four distinct split strategies, and calculate deterministic, debt-minimized settlement transfers (who owes whom).

The system integrates Google Gemini Vision for document comprehension with an offline heuristic fallback, ensuring that application workflows never crash even under API rate limits or network disruptions.

---

## 2. Key Features

- **Document & Multi-Bill OCR**:
  - Process JPG, JPEG, PNG, WEBP, and PDF invoices.
  - Concurrent multi-bill processing: isolates each receipt independently while providing an aggregate combined total.
  - Five-stage visual extraction progression: Uploading → Processing → Extracting → Validating → Completed (with real-time error retries).
- **Machine Learning Classification**:
  - scikit-learn TF-IDF Vectorizer + Logistic Regression trained on 1,600+ synthetic financial records.
  - Classifies 12 financial sectors: *Food & Dining*, *Groceries*, *Shopping*, *Transport*, *Fuel*, *Healthcare*, *Entertainment*, *Utilities*, *Travel*, *Education*, *Bills*, and *Other*.
  - Reports calibrated prediction confidence scores.
- **Natural Language Parsing (NLP)**:
  - Deterministic regex & NLP extraction from quick notes like: `"Chaitu paid 1200 for dinner at Pizza Hut"`.
- **Participant & Payer Management**:
  - Add individual or comma-separated names (e.g. `Chaitu, Ramu, Mohan, Lathi`).
  - Active participant state persists across all 4 steps of the wizard.
  - Interactive payer selector dynamically changes who is owed money in final settlement calculations.
- **4 Split Strategies**:
  1. **Equal Split**: Even division with deterministic odd-cent remainder balancing.
  2. **Percentage Split**: Custom percentage per person (strict 100.0% validation).
  3. **Custom Amount**: Exact rupee values per person (validates sum == bill total).
  4. **Itemized Split**: Assign individual receipt items to specific participants with proportional tax and surcharge apportionment.
- **Deterministic Settlement Engine**:
  - Greedy debt-simplification algorithm minimizing the total number of cash transfers.
  - Positive balance = creditor (receives money); Negative balance = debtor (owes money).
  - Uses exact Decimal integer-cents arithmetic to eliminate IEEE-754 floating point drift.
- **AI Financial Assistant**:
  - Grounded in real-time user database figures (spending by category, monthly budget, pending debts).
  - Answers questions like: *"How much did I spend this month?"*, *"What is my highest spending category?"*, *"How much does Ramu owe me?"*.
- **Smart Buy AI**:
  - Evaluates big-ticket purchase affordability against remaining monthly budget, savings runway, and daily pacing.
- **Budget Insights**:
  - Set total monthly budget and category-specific thresholds with visual warning limits (safe < 80%, warning 80-90%, exceeded > 100%).
- **Interactive Analytics (Recharts)**:
  - 6-Month Spending Trends (Area chart).
  - Category Distribution (Donut chart).
  - 14-Day Daily Outlays (Bar chart).
  - Budget Limit vs. Actual Outlay (Grouped bar chart).
- **Multi-Format Export Engine**:
  - Polished PDF settlement reports via `jsPDF` and `jspdf-autotable`.
  - Plain-text TXT settlement sheets for WhatsApp and SMS sharing.
  - CSV expense ledger export.

---

## 3. Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Tooling & Bundler**: Vite
- **Styling**: Tailwind CSS (Dark fintech aesthetic: `#0B0F19`, `#111827`, Indigo `#6366F1`, Purple `#8B5CF6`, Emerald `#10B981`)
- **Icons**: Lucide React
- **Visualizations**: Recharts
- **State Management**: Zustand (Centralized `useExpenseWorkflowStore` persisting wizard state)
- **Document Export**: jsPDF + jspdf-autotable
- **Markdown**: react-markdown

### Backend
- **Language**: Python 3.13
- **Web Framework**: Flask 3.1
- **CORS & Sessions**: Flask-CORS, Flask-Login
- **ORM & Database**: Flask-SQLAlchemy with SQLite3
- **Document Processing**: Pillow (PIL), pypdf

### Machine Learning & NLP
- **scikit-learn**: TF-IDF n-grams (1, 2) + Logistic Regression (class_weight='balanced')
- **NLP**: Heuristic Regex Extractor + spaCy-compatible pattern matcher
- **Serialization**: joblib

### Companion Gateway Server
- **Runtime**: Node.js + Express
- **Language**: TypeScript
- **Security**: Helmet, CORS

---

## 4. Project Architecture

```
anika-ai/
│
├── src/                               # React + TypeScript + Vite Frontend
│   ├── components/
│   │   ├── common/                    # Navbar, Sidebar, StatCard, Badge, Modal, Toast
│   │   ├── ocr/                       # UploadDropzone, MultiBillViewer
│   │   ├── split/                     # 4-Step Wizard:
│   │   │                              # Step 1: Preview & Edit Items
│   │   │                              # Step 2: Participant Management (Chaitu, Ramu, Mohan, Lathi)
│   │   │                              # Step 3: Split Strategy (Equal, %, Custom, Itemized) & Payer
│   │   │                              # Step 4: Final Settlement & Save
│   │   ├── analytics/                 # SpendingTrendChart, CategoryPieChart, DailySpendBarChart
│   │   ├── advisor/                   # ChatAdvisor (Grounded AI chat)
│   │   └── smartbuy/                  # SmartBuyCard (Affordability evaluator)
│   ├── pages/                         # DashboardPage, OCRScannerPage, SplitBillPage, ExpensesPage, BudgetPage, SmartBuyPage, ActivityLogsPage, AnalyticsPage, SettingsPage, AuthModal
│   ├── services/                      # api.ts, ocrService.ts, expenseService.ts, exportService.ts
│   ├── store/                         # expenseWorkflowStore.ts, authStore.ts
│   ├── types/                         # TypeScript interfaces
│   ├── utils/                         # currency.ts (₹ INR), calculations.ts
│   ├── App.tsx                        # Master layout & navigation
│   ├── index.css                      # Tailwind & Glassmorphism styles
│   └── main.tsx                       # React root entry
│
├── backend/                           # Python Flask API & ML Pipeline
│   ├── models/                        # SQLAlchemy Models: User, Expense, ExpenseItem, Participant, Split, Settlement, Receipt, Budget, ActivityLog, AIInsight
│   ├── routes/                        # Blueprints: auth, ocr, split, settlement, expense, dashboard, analytics, budget, ai, export
│   ├── services/                      # settlement_engine.py, split_calculator.py, gemini_service.py, ocr_parser.py, nlp_service.py, smart_buy_engine.py
│   ├── ml/                            # train_category_model.py, predictor.py
│   ├── ocr/                           # processor.py (image preprocessor)
│   ├── utils/                         # logger.py, helpers.py, auth_decorators.py
│   ├── datasets/                      # expense_categories_dataset.csv (1620 records)
│   ├── trained_models/                # category_model.pkl
│   ├── config.py                      # App configuration
│   ├── extensions.py                  # db, login_manager, cors
│   └── app.py                         # Flask application factory
│
├── server/                            # Node.js + Express companion server
│   ├── routes/                        # api.ts
│   ├── services/                      # stats.ts
│   ├── db.ts                          # database connectivity check
│   ├── index.ts                       # Express setup with Helmet & CORS
│   └── utils.ts
│
├── uploads/                           # Temporary receipt upload directory
├── tests/                             # Pytest automated test suite (29 tests)
│   ├── test_splits.py                 # Equal, %, Custom, Itemized split tests
│   ├── test_settlement.py             # Greedy debt minimization tests
│   ├── test_ml_and_nlp.py             # ML inference & NLP parser tests
│   └── test_auth_and_api.py           # Registration, login, CRUD, dashboard, budget tests
│
├── .env.example                       # Documented environment variables
├── .gitignore
├── package.json                       # Frontend & Node dependencies
├── requirements.txt                   # Python backend dependencies
├── pytest.ini                         # Pytest configuration
├── tsconfig.json                      # TypeScript configuration
└── vite.config.ts                     # Vite build configuration with API proxy
```

---

## 5. Database Schema (SQLite)

1. **`users`**: `id`, `username`, `email`, `password_hash`, `full_name`, `currency`, `monthly_budget`, `created_at`.
2. **`expenses`**: `id`, `user_id`, `title`, `merchant_name`, `transaction_date`, `currency`, `subtotal`, `tax`, `gst`, `total_amount`, `category`, `split_strategy`, `payer_id`, `payer_name`, `notes`, `status`, `created_at`.
3. **`expense_items`**: `id`, `expense_id`, `name`, `quantity`, `unit_price`, `total_price`, `category`, `assigned_participants`.
4. **`participants`**: `id`, `expense_id`, `participant_key`, `name`, `email`, `phone`, `is_payer`.
5. **`splits`**: `id`, `expense_id`, `participant_key`, `participant_name`, `share_amount`, `share_percentage`, `item_ids_json`.
6. **`settlements`**: `id`, `expense_id`, `from_participant_key`, `from_name`, `to_participant_key`, `to_name`, `amount`, `is_paid`, `paid_at`, `payment_reference`.
7. **`receipts`**: `id`, `user_id`, `expense_id`, `file_path`, `original_filename`, `mime_type`, `file_size`, `raw_extracted_json`, `ocr_confidence`, `upload_date`.
8. **`budgets`**: `id`, `user_id`, `month`, `year`, `total_budget`, `category_budgets_json`, `created_at`, `updated_at`.
9. **`activity_logs`**: `id`, `user_id`, `action_type`, `description`, `metadata_json`, `timestamp`.
10. **`ai_insights`**: `id`, `user_id`, `insight_type`, `content`, `recommendations_json`, `created_at`.

---

## 6. Installation & Quickstart

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ & npm

### Setup Environment
1. Clone repository and navigate to root directory:
```bash
git clone https://github.com/example/anika-ai.git
cd anika-ai
```

2. Configure environment variables:
```bash
cp .env.example .env
```

3. Python Backend Setup:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

4. Frontend Setup:
```bash
npm install
```

---

## 7. Run Commands

### 1. Train the ML Category Model
```bash
.venv\Scripts\python.exe backend/ml/train_category_model.py
```
*Generates 1,600+ synthetic financial transactions and serializes `backend/trained_models/category_model.pkl`.*

### 2. Run Automated Tests
```bash
.venv\Scripts\pytest.exe -v
```
*Runs all 29 automated tests verifying splits, debt settlements, ML classification, NLP extraction, authentication, and REST endpoints.*

### 3. Start Backend Flask Server (Port 5000)
```bash
.venv\Scripts\python.exe backend/app.py
```

### 4. Start Frontend Vite Development Server (Port 5173)
```bash
npm run dev
```

### 5. (Optional) Start Node.js Companion Server (Port 5001)
```bash
npm run server
```

Open your browser at **`http://localhost:5173`**.

---

## 8. Verification & Testing Summary

All 29 test cases execute with 100% pass rate:
- **`tests/test_splits.py`**:
  - `test_equal_split_even_division` (PASSED)
  - `test_equal_split_odd_cent_remainder_balanced` (PASSED)
  - `test_equal_split_four_participants` (PASSED)
  - `test_equal_split_invalid_inputs` (PASSED)
  - `test_percentage_split_valid` (PASSED)
  - `test_percentage_split_invalid_sum` (PASSED)
  - `test_custom_split_valid` (PASSED)
  - `test_custom_split_mismatch_rejection` (PASSED)
  - `test_itemized_split_with_proportional_tax` (PASSED)
- **`tests/test_settlement.py`**:
  - `test_settlement_payer_chaitu_four_people` (PASSED)
  - `test_settlement_payer_ramu_custom_amounts` (PASSED)
  - `test_net_balance_conservation` (PASSED)
  - `test_debt_minimization_reduces_transactions` (PASSED)
- **`tests/test_ml_and_nlp.py`**:
  - `test_ml_prediction_fuel` (PASSED)
  - `test_ml_prediction_food_and_dining` (PASSED)
  - `test_ml_prediction_shopping` (PASSED)
  - `test_ml_prediction_healthcare` (PASSED)
  - `test_ml_prediction_entertainment` (PASSED)
  - `test_nlp_extraction_chaitu_dinner` (PASSED)
  - `test_nlp_extraction_with_merchant` (PASSED)
- **`tests/test_auth_and_api.py`**:
  - `test_password_hashing` (PASSED)
  - `test_api_health` (PASSED)
  - `test_auth_login_success` (PASSED)
  - `test_auth_login_invalid_password` (PASSED)
  - `test_auth_register_new_user` (PASSED)
  - `test_create_expense_workflow` (PASSED)
  - `test_dashboard_api` (PASSED)
  - `test_budget_api_get_and_post` (PASSED)
  - `test_smartbuy_api` (PASSED)

---

## 9. Honest Attribution & Acknowledgments

Initial UI scaffolding/prototyping was assisted using Google AI Studio/AI coding tools, while the application architecture, integrations, backend logic, ML/OCR workflows, debugging, testing, and feature implementation were developed and refined as part of the project.

---

## 10. Author & License

Developed with ❤️ for financial intelligence and seamless expense management.
Licensed under the MIT License.
