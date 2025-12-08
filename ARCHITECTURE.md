# NBFC Agentic AI System - Architecture & Technical Documentation

**Version**: 2.0  
**Last Updated**: December 2025  
**Status**: ✅ Fully Functional MVP with Enhanced Verification

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React + Vite Frontend)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Chat         │  │ File Upload  │  │ Sanction     │         │
│  │ Interface    │  │ Component    │  │ Download     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    MASTER AGENT                          │  │
│  │              (Orchestrator & Controller)                 │  │
│  │  • Conversation Management                               │  │
│  │  • State Machine Control                                 │  │
│  │  • Worker Agent Delegation                               │  │
│  │  • Memory Management                                     │  │
│  └────┬─────────────────────────────────────────────────────┘  │
│       │                                                         │
│       ├─────────────┬──────────────┬──────────────┬───────────┤
│       ▼             ▼              ▼              ▼           │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Sales   │  │Verification│ │Underwriting│ │Sanction  │      │
│  │ Agent   │  │  Agent    │  │  Agent    │  │  Agent   │      │
│  └─────────┘  └──────────┘  └──────────┘  └──────────┘      │
│       │             │              │              │           │
│       └─────────────┴──────────────┴──────────────┘           │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  MOCK SERVICES LAYER                     │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│  │  │   CRM    │  │  Credit  │  │  Offer   │              │  │
│  │  │ Service  │  │  Bureau  │  │   Mart   │              │  │
│  │  └──────────┘  └──────────┘  └──────────┘              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   UTILITY LAYER                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│  │
│  │  │   EMI    │  │  Salary  │  │   PDF    │  │  Name   ││  │
│  │  │Calculator│  │  Parser  │  │Generator │  │Verifier ││  │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘│  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Customer   │  │   Uploaded   │  │  Sanction    │         │
│  │     Data     │  │    Files     │  │   Letters    │         │
│  │ (mock_data)  │  │  (uploads/)  │  │(sanctions/)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conversation Flow State Machine

```
┌─────────────┐
│  GREETING   │ ◄─── Initial greeting + phone number request
└──────┬──────┘      (Combined in single message)
       │
       ▼
┌─────────────────┐
│ INTENT_CAPTURE  │ ◄─── Validate phone number
└──────┬──────────┘
       │
       ▼
┌──────────────────────┐
│ LEAD_QUALIFICATION   │ ◄─── Fetch from CRM
└──────┬───────────────┘
       │
       ├─── Customer Not Found ──► CLOSE
       │
       ▼
┌──────────────────────┐
│ OFFER_PRESENTATION   │ ◄─── Present loan offer
└──────┬───────────────┘
       │
       ├─── Can loop for tenure changes
       │
       ▼
┌──────────────────────┐
│ KYC_VERIFICATION     │ ◄─── Verify identity
└──────┬───────────────┘      Upload salary slip
       │
       ├─── Can loop for OTP/documents
       │
       ▼
┌──────────────────────┐
│   UNDERWRITING       │ ◄─── Apply business rules
└──────┬───────────────┘
       │
       ├─── Conditional ──► Back to KYC (salary slip)
       │
       ▼
┌──────────────────────┐
│     DECISION         │
└──────┬───────────────┘
       │
       ├─── Approved ──┐
       │               │
       │               ▼
       │         ┌──────────────────┐
       │         │ SANCTION_LETTER  │
       │         └────────┬─────────┘
       │                  │
       ├─── Rejected ─────┤
       │                  │
       ▼                  ▼
    ┌──────────────────────┐
    │       CLOSE          │
    └──────────────────────┘
```

---

## Worker Agent Responsibilities

### 1. Sales Agent
**Purpose**: Maximize conversion through persuasive sales tactics

**Capabilities**:
- Present personalized loan offers based on credit score
- Calculate EMI and total payable amount
- Handle tenure change requests
- Manage objections (high EMI, high rate)
- Negotiate terms within business rules

**Key Methods**:
- `present_offer()` - Create and present loan offer
- `handle_tenure_change()` - Recalculate with new tenure
- `handle_objection()` - Address customer concerns

---

### 2. Verification Agent
**Purpose**: Ensure customer identity and income verification

**Capabilities**:
- Verify KYC status from CRM
- Simulate OTP verification
- Request salary slip upload
- Validate uploaded documents (format, size)
- **AI-powered name verification** using OpenRouter API
- Confirm salary verification

**Key Methods**:
- `verify_kyc()` - Check KYC status
- `simulate_otp_verification()` - Mock OTP flow
- `request_salary_slip()` - Ask for income proof
- `validate_uploaded_file()` - Check file validity
- `verify_names_match()` - AI verification of name matching
- `confirm_salary_verification()` - Acknowledge receipt

**Name Verification**:
- Uses OpenRouter AI API (model: `openai/gpt-oss-20b:free`)
- Compares customer name from CRM with name on salary slip
- Handles variations, nicknames, and different name formats
- Returns confidence score and detailed reasoning for mismatches
- Rejects salary slips with non-matching names

---

### 3. Underwriting Agent
**Purpose**: Risk assessment and loan approval decision

**Business Rules**:
```python
if credit_score < 700:
    return REJECTED  # Reason: LOW_CREDIT_SCORE

if requested_amount <= pre_approved_limit:
    return APPROVED  # Reason: PRE_APPROVED

if requested_amount <= 2 × pre_approved_limit:
    if salary_slip_not_uploaded:
        return CONDITIONAL  # Reason: SALARY_VERIFICATION_REQUIRED
    
    emi = calculate_emi(amount, rate, tenure)
    emi_ratio = emi / monthly_salary
    
    if emi_ratio <= 0.50:
        return APPROVED  # Reason: APPROVED_WITH_SALARY_VERIFICATION
    else:
        return REJECTED  # Reason: HIGH_EMI_TO_SALARY_RATIO

if requested_amount > 2 × pre_approved_limit:
    return REJECTED  # Reason: AMOUNT_EXCEEDS_LIMIT
```

**Key Methods**:
- `evaluate_loan()` - Main decision logic
- `_craft_approval_message()` - Success message
- `_craft_rejection_message()` - Rejection with reason
- `_craft_conditional_message()` - Request additional docs

---

### 4. Sanction Agent
**Purpose**: Generate official loan sanction documentation

**Capabilities**:
- Generate unique sanction IDs
- Create professional PDF sanction letters
- Include all loan terms and conditions
- Provide download links

**Key Methods**:
- `generate_sanction_letter()` - Create PDF
- `craft_sanction_message()` - Delivery message

**PDF Contents**:
- Company header and branding
- Sanction ID and date
- Customer details
- Loan amount, tenure, interest rate
- EMI and total payable
- Terms and conditions
- Processing fee details
- Contact information

---

## Low-Level Architecture

### File & Module Organization

```
backend/
├── main.py                      # FastAPI application entry point
├── config.py                    # Configuration management
├── models.py                    # Pydantic data models
├── master_agent.py              # Main orchestrator (MasterAgent class)
├── state_machine.py             # State transition logic
├── memory_manager.py            # Session & context management
│
├── agents/                      # Worker agents directory
│   ├── __init__.py
│   ├── sales_agent.py          # SalesAgent class
│   ├── verification_agent.py   # VerificationAgent class
│   ├── underwriting_agent.py   # UnderwritingAgent class
│   └── sanction_agent.py       # SanctionAgent class
│
├── mocks/                       # Mock service layer
│   ├── __init__.py
│   ├── crm_service.py          # CRMService (singleton)
│   ├── credit_bureau.py        # CreditBureauService (singleton)
│   └── offer_mart.py           # OfferMartService (singleton)
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   ├── emi_calculator.py       # EMI calculation functions
│   ├── salary_parser.py        # Salary slip OCR mock
│   ├── name_verifier.py        # AI-powered name matching
│   └── sanction_letter_generator.py  # PDF generation
│
└── requirements.txt             # Python dependencies

frontend/
├── index.html                   # HTML entry point
├── vite.config.js              # Vite build configuration
├── package.json                # Node dependencies
│
└── src/
    ├── main.jsx                # React entry point
    ├── App.jsx                 # Main application component
    ├── App.css                 # Application styles
    ├── index.css               # Global styles & design system
    │
    └── components/
        ├── ChatInterface.jsx   # Main chat container
        ├── ChatInterface.css
        ├── MessageBubble.jsx   # Individual message display
        ├── MessageBubble.css
        ├── FileUpload.jsx      # File upload component
        └── FileUpload.css

data/
├── mock_data.json              # Customer profiles (10 records)
└── sanction_letters/           # Generated PDFs

uploads/                         # Uploaded salary slips
```

---

### Class Diagrams

#### Master Agent & State Management

```
┌─────────────────────────────────────────────────────────┐
│                    MasterAgent                          │
├─────────────────────────────────────────────────────────┤
│ - memory_manager: MemoryManager                         │
│ - state_machine: StateMachine                           │
├─────────────────────────────────────────────────────────┤
│ + process_message(message: ChatMessage) → ChatResponse │
│ - _handle_greeting() → ChatResponse                    │
│ - _handle_intent_capture() → ChatResponse              │
│ - _handle_lead_qualification() → ChatResponse          │
│ - _handle_offer_presentation() → ChatResponse          │
│ - _handle_kyc_verification() → ChatResponse            │
│ - _handle_underwriting() → ChatResponse                │
│ - _handle_decision() → ChatResponse                    │
│ - _handle_sanction_letter() → ChatResponse             │
│ - _handle_close() → ChatResponse                       │
│ - _extract_phone(text: str) → Optional[str]            │
│ - _extract_amount(text: str) → Optional[float]         │
│ - _extract_tenure(text: str) → Optional[int]           │
└─────────────────────────────────────────────────────────┘
                    │
                    │ uses
                    ▼
┌─────────────────────────────────────────────────────────┐
│                 MemoryManager                           │
├─────────────────────────────────────────────────────────┤
│ - sessions: Dict[str, ConversationMemory]               │
├─────────────────────────────────────────────────────────┤
│ + create_session() → str                                │
│ + get_session(session_id: str) → ConversationMemory    │
│ + update_session(session_id: str, memory)              │
│ + set_customer(session_id: str, customer: Customer)    │
│ + set_application(session_id: str, app: LoanApp)       │
│ + add_message(session_id: str, role, content)          │
│ + update_context(session_id: str, key, value)          │
│ + get_context(session_id: str, key) → Any              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  StateMachine                           │
├─────────────────────────────────────────────────────────┤
│ - TRANSITIONS: Dict[Stage, List[Stage]]                 │
├─────────────────────────────────────────────────────────┤
│ + can_transition(current, next) → bool                  │
│ + transition(memory, next_stage) → bool                 │
│ + get_next_stage(current, context) → Stage             │
└─────────────────────────────────────────────────────────┘
```

#### Worker Agents

```
┌─────────────────────────────────────────────────────────┐
│                    SalesAgent                           │
├─────────────────────────────────────────────────────────┤
│ + present_offer(customer, amount, tenure) → dict        │
│ + handle_tenure_change(customer, amount, new_tenure)   │
│ + handle_objection(objection_type: str) → str          │
│ - _calculate_interest_rate(credit_score: int) → float  │
│ - _craft_offer_message(offer: OfferDetails) → str      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               VerificationAgent                         │
├─────────────────────────────────────────────────────────┤
│ + verify_kyc(customer: Customer) → dict                 │
│ + simulate_otp_verification(customer) → dict            │
│ + request_salary_slip(customer, reason) → str           │
│ + validate_uploaded_file(filename, size) → dict         │
│ + confirm_salary_verification(salary, name) → str       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              UnderwritingAgent                          │
├─────────────────────────────────────────────────────────┤
│ + evaluate_loan(customer, amount, tenure, salary) → dict│
│ - _craft_approval_message(customer, amount) → str       │
│ - _craft_rejection_message(customer, reason) → str      │
│ - _craft_conditional_message(customer) → str            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 SanctionAgent                           │
├─────────────────────────────────────────────────────────┤
│ + generate_sanction_letter(customer, app, offer) → obj  │
│ + craft_sanction_message(customer, id, url, offer) → str│
│ - _generate_sanction_id() → str                         │
└─────────────────────────────────────────────────────────┘
```

---

### Sequence Diagrams

#### Instant Approval Flow

```
User          Frontend       Backend        MasterAgent    CRMService    SalesAgent    UnderwritingAgent    SanctionAgent
 │                │              │               │              │             │                 │                 │
 │──Start Chat───>│              │               │              │             │                 │                 │
 │                │──POST /start─>│               │              │             │                 │                 │
 │                │              │──process()───>│              │             │                 │                 │
 │                │              │               │─greeting()   │             │                 │                 │
 │                │<─greeting+ph─│<──────────────│              │             │                 │                 │
 │<──Display──────│              │               │              │             │                 │                 │
 │                │              │               │              │             │                 │                 │
 │──9876543211───>│              │               │              │             │                 │                 │
 │                │──POST /chat──>│               │              │             │                 │                 │
 │                │              │──process()───>│              │             │                 │                 │
 │                │              │               │──get_by_ph()─>│             │                 │                 │
 │                │              │               │<─customer────│             │                 │                 │
 │                │              │               │─qualify()    │             │                 │                 │
 │                │<──welcome────│<──────────────│              │             │                 │                 │
 │<──Display──────│              │               │              │             │                 │                 │
 │                │              │               │              │             │                 │                 │
 │──300k/24m─────>│              │               │              │             │                 │                 │
 │                │──POST /chat──>│               │              │             │                 │                 │
 │                │              │──process()───>│              │             │                 │                 │
 │                │              │               │────────────present_offer()──>│                 │                 │
 │                │              │               │<──────────────offer_details──│                 │                 │
 │                │<──offer──────│<──────────────│              │             │                 │                 │
 │<──Display──────│              │               │              │             │                 │                 │
 │                │              │               │              │             │                 │                 │
 │──yes──────────>│              │               │              │             │                 │                 │
 │                │──POST /chat──>│               │              │             │                 │                 │
 │                │              │──process()───>│              │             │                 │                 │
 │                │              │               │─verify_kyc() │             │                 │                 │
 │                │              │               │──────────────evaluate_loan()──────────────────>│                 │
 │                │              │               │<──────────────APPROVED────────────────────────│                 │
 │                │              │               │───────────────generate_sanction()─────────────────────────────>│
 │                │              │               │<──────────────sanction.pdf────────────────────────────────────│
 │                │<─approval+pdf─│<──────────────│              │             │                 │                 │
 │<──Display──────│              │               │              │             │                 │                 │
```

#### Conditional Approval with Salary Slip

```
User        Frontend      Backend      MasterAgent  UnderwritingAgent  VerificationAgent  NameVerifier
 │              │             │              │              │                  │                │
 │──500k/36m───>│             │              │              │                  │                │
 │              │──POST /chat─>│              │              │                  │                │
 │              │             │──process()──>│              │                  │                │
 │              │             │              │───evaluate()─>│                  │                │
 │              │             │              │<─CONDITIONAL──│                  │                │
 │              │             │              │───request_salary_slip()────────>│                │
 │              │<─upload_req─│<─────────────│              │                  │                │
 │<─Display─────│             │              │              │                  │                │
 │              │             │              │              │                  │                │
 │──salary.pdf─>│             │              │              │                  │                │
 │              │──POST /upload>              │              │                  │                │
 │              │             │───validate()──────────────────────────────────>│                │
 │              │             │───parse()─────────────────────────────────────>│                │
 │              │             │<──parsed_data─────────────────────────────────│                │
 │              │             │───verify_names(CRM_name, Slip_name)───────────────────────────>│
 │              │             │<──match_result────────────────────────────────────────────────│
 │              │             │              │              │                  │                │
 │              │             │──re_eval()──>│──evaluate()─>│                  │                │
 │              │             │              │<─APPROVED────│                  │                │
 │              │<─approval───│<─────────────│              │                  │                │
 │<─Display─────│             │              │              │                  │                │
```

---

### Data Flow Architecture

#### Session Data Flow

```
1. Session Creation:
   POST /api/chat/start
   └─> MemoryManager.create_session()
       └─> Generate UUID
       └─> Initialize ConversationMemory
           ├─> session_id: str
           ├─> phone: None
           ├─> customer: None
           ├─> application: None
           ├─> current_stage: GREETING
           ├─> conversation_history: []
           └─> context: {}
       └─> Store in sessions dict
       └─> Return session_id + greeting

2. Message Processing:
   POST /api/chat {session_id, message}
   └─> MasterAgent.process_message()
       ├─> Retrieve session from MemoryManager
       ├─> Add user message to history
       ├─> Route to stage handler
       │   └─> _handle_<stage>(message, memory)
       │       ├─> Extract data (phone, amount, tenure)
       │       ├─> Call worker agents if needed
       │       ├─> Update application state
       │       ├─> Transition state if needed
       │       └─> Return ChatResponse
       ├─> Add assistant message to history
       └─> Return response to frontend

3. Context Updates:
   Throughout conversation:
   └─> MemoryManager.update_context(session_id, key, value)
       └─> memory.context[key] = value
       Examples:
       ├─> 'kyc_verified': True
       ├─> 'offer_presented': True
       ├─> 'awaiting_salary_slip': True
       └─> 'decision': 'approved'
```

#### File Upload Data Flow

```
1. Frontend uploads file:
   POST /api/upload?session_id=xxx
   FormData: {file: salary.pdf}

2. Backend processing:
   main.py:upload_file()
   │
   ├─> Read file content
   ├─> Validate file (VerificationAgent)
   │   ├─> Check extension (.pdf)
   │   └─> Check size (<5MB)
   │
   ├─> Save to uploads/ directory
   │   └─> filename: {uuid}.pdf
   │
   ├─> Parse salary slip (SalaryParser)
   │   └─> Extract: employee_name, monthly_salary
   │
   ├─> Verify name match (NameVerifier)
   │   ├─> Get customer name from memory
   │   ├─> Call OpenRouter API
   │   └─> Return: {match: bool, confidence: float, reason: str}
   │
   ├─> If name mismatch:
   │   └─> Return error + ask for correct document
   │
   ├─> If name matches:
   │   ├─> Update application.parsed_salary
   │   ├─> Update application.salary_slip_uploaded = True
   │   ├─> Re-run underwriting
   │   └─> Return approval/rejection
   │
   └─> Return response
```

---

### API Request/Response Flow

#### Detailed Endpoint Specifications

**1. Start Chat Session**
```http
POST /api/chat/start
```
**Request:** None (empty body)

**Response:**
```json
{
  "session_id": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9",
  "message": "🙏 **Welcome to Tata Capital!**\n\nHello! I'm your personal loan assistant...\n\n**To get started, please enter your 10-digit mobile number (e.g., 9876543210):**",
  "stage": "intent_capture"
}
```

**2. Send Message**
```http
POST /api/chat
Content-Type: application/json
```
**Request:**
```json
{
  "session_id": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9",
  "message": "9876543210"
}
```

**Response:**
```json
{
  "session_id": "d4e5f6g7-h8i9-j0k1-l2m3-n4o5p6q7r8s9",
  "message": "✅ **Welcome back, Priya Sharma!**\n\nGreat news! You have a **pre-approved loan offer**...",
  "stage": "offer_presentation",
  "requires_input": true,
  "input_type": "text",
  "choices": null,
  "metadata": null
}
```

**3. Upload Salary Slip**
```http
POST /api/upload?session_id={session_id}
Content-Type: multipart/form-data
```
**Request:**
```
file: [Binary PDF data]
```

**Response (Success):**
```json
{
  "success": true,
  "message": "✅ **Salary Verified**\n\nThank you for uploading your salary slip...",
  "parsed_salary": 85000,
  "stage": "sanction_letter",
  "metadata": {
    "sanction_id": "D4E5F6G7",
    "pdf_url": "/api/sanction/download/D4E5F6G7"
  }
}
```

**Response (Name Mismatch):**
```json
{
  "success": false,
  "message": "❌ **Name Verification Failed**\n\nThe name on the salary slip doesn't match your customer profile...",
  "name_mismatch": true,
  "customer_name": "Priya Sharma",
  "salary_slip_name": "P. S. Verma"
}
```

**4. Download Sanction Letter**
```http
GET /api/sanction/generate/{session_id}
```
**Response:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename=sanction_{id}.pdf
[Binary PDF data]
```

---

### State Transition Logic

```python
# state_machine.py

TRANSITIONS = {
    GREETING: [INTENT_CAPTURE],
    
    INTENT_CAPTURE: [LEAD_QUALIFICATION],
    
    LEAD_QUALIFICATION: [
        OFFER_PRESENTATION,  # Customer found
        CLOSE                # Customer not found
    ],
    
    OFFER_PRESENTATION: [
        KYC_VERIFICATION,    # Offer accepted
        OFFER_PRESENTATION   # Tenure change (loop)
    ],
    
    KYC_VERIFICATION: [
        UNDERWRITING,        # KYC verified
        KYC_VERIFICATION     # Loop for OTP/docs
    ],
    
    UNDERWRITING: [
        DECISION,            # Evaluated
        KYC_VERIFICATION     # Need salary slip (back)
    ],
    
    DECISION: [
        SANCTION_LETTER,     # Approved
        CLOSE                # Rejected
    ],
    
    SANCTION_LETTER: [CLOSE],
    
    CLOSE: []                # Terminal state
}

def transition(memory, next_stage):
    """
    Validates and executes state transition
    
    Returns:
        True if transition successful
        False if invalid transition
    """
    if next_stage in TRANSITIONS[memory.current_stage]:
        memory.current_stage = next_stage
        return True
    return False
```

---

### Memory & Context Management

```python
# memory_manager.py

class MemoryManager:
    def __init__(self):
        self.sessions = {}  # Dict[session_id, ConversationMemory]
    
    def create_session(self) -> str:
        """Create new session with unique ID"""
        session_id = str(uuid.uuid4())
        memory = ConversationMemory(
            session_id=session_id,
            current_stage=ConversationStage.GREETING
        )
        self.sessions[session_id] = memory
        return session_id
    
    def get_session(self, session_id: str):
        """Retrieve session memory"""
        return self.sessions.get(session_id)
    
    def update_context(self, session_id, key, value):
        """Update session context"""
        if session_id in self.sessions:
            self.sessions[session_id].context[key] = value
    
    def set_customer(self, session_id, customer):
        """Set customer data in session"""
        if session_id in self.sessions:
            self.sessions[session_id].customer = customer
    
    def set_application(self, session_id, application):
        """Set loan application in session"""
        if session_id in self.sessions:
            self.sessions[session_id].application = application

# Singleton instance
memory_manager = MemoryManager()
```

**Context Keys Used:**
```python
context = {
    'phone': '9876543210',
    'kyc_checked': True,
    'kyc_verified': True,
    'offer_presented': True,
    'current_offer': OfferDetails(...),
    'awaiting_salary_slip': True,
    'salary_verified': True,
    'name_mismatch_detected': False,
    'decision': 'approved'
}
```

---

### Frontend Component Architecture

```
App.jsx (Root)
│
├─ State:
│  ├─ sessionId: string
│  ├─ initialMessage: string
│  └─ isLoading: boolean
│
├─ useEffect: startNewSession()
│  └─> fetch('/api/chat/start')
│      └─> setSessionId()
│      └─> setInitialMessage()
│
└─> <ChatInterface 
      sessionId={sessionId}
      initialMessage={initialMessage} />
    │
    ├─ State:
    │  ├─ messages: Array<Message>
    │  ├─ inputValue: string
    │  ├─ isLoading: boolean
    │  ├─ currentStage: string
    │  ├─ requiresFileUpload: boolean
    │  └─ sanctionData: object
    │
    ├─ useEffect: Display initial message
    │  └─> setMessages([initialMessage])
    │
    ├─ sendMessage(text)
    │  └─> POST /api/chat
    │      └─> Update messages
    │      └─> Update stage
    │      └─> Check for file upload requirement
    │
    ├─ handleFileUpload(file)
    │  └─> POST /api/upload
    │      └─> Update messages
    │      └─> Update stage
    │
    └─> Components:
        │
        ├─> <MessageBubble 
        │     role={message.role}
        │     content={message.content} />
        │
        ├─> <FileUpload 
        │     onFileSelect={handleFileUpload}
        │     disabled={isLoading} />
        │
        └─> Download Button (if sanctionData)
```

---

### Error Handling & Edge Cases

**1. Session Not Found**
```python
if not memory:
    raise HTTPException(status_code=404, detail="Session not found")
```

**2. Invalid Phone Number**
```python
phone = _extract_phone(message)
if not phone:
    return ChatResponse(
        message="Please enter a valid 10-digit mobile number",
        stage=INTENT_CAPTURE
    )
```

**3. Customer Not Found in CRM**
```python
customer = crm_service.get_customer_by_phone(phone)
if not customer:
    return ChatResponse(
        message="Customer not found. Please contact support.",
        stage=CLOSE,
        requires_input=False
    )
```

**4. File Upload Validation**
```python
if not filename.endswith('.pdf'):
    return {"success": False, "message": "Only PDF files allowed"}

if file_size > 5_000_000:  # 5MB
    return {"success": False, "message": "File too large (max 5MB)"}
```

**5. Name Mismatch Handling**
```python
verification = verify_names_match(customer_name, employee_name)
if not verification['match']:
    return {
        "success": False,
        "message": "Name verification failed",
        "name_mismatch": True
    }
```

**6. State Transition Errors**
```python
if not state_machine.can_transition(current, next):
    logger.error(f"Invalid transition: {current} -> {next}")
    # Gracefully continue with current stage
    return ChatResponse(stage=current, ...)
```

---

### Performance Optimization Strategies

**1. Async Operations**
```python
# FastAPI async endpoints
@app.post("/api/chat")
async def chat(message: ChatMessage):
    response = master_agent.process_message(message)
    return response
```

**2. Caching**
```python
# Cache customer data within session
# Avoid repeated CRM lookups
if memory.customer:
    customer = memory.customer  # Use cached
else:
    customer = crm_service.get_customer_by_phone(phone)
    memory_manager.set_customer(session_id, customer)
```

**3. Lazy Loading**
```python
# Only load PDF generator when needed
if decision == APPROVED:
    from agents.sanction_agent import sanction_agent
    sanction_agent.generate_sanction_letter(...)
```

**4. Frontend Optimization**
```javascript
// Debounce input to avoid excessive API calls
const debouncedSend = debounce(sendMessage, 300);

// Virtual scrolling for long conversations
// Only render visible messages
```

---

### Security Implementation Details

**1. Input Validation (Pydantic)**
```python
class ChatMessage(BaseModel):
    session_id: str
    message: str
    phone: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if len(v) > 1000:
            raise ValueError('Message too long')
        return v.strip()
```

**2. File Upload Security**
```python
# Check file signature (magic number)
def is_valid_pdf(file_content):
    return file_content[:4] == b'%PDF'

# Sanitize filename
safe_filename = f"{uuid.uuid4()}{Path(filename).suffix}"
```

**3. CORS Configuration**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**4. AI Name Verification**
```python
# Call OpenRouter with retry logic
try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "openai/gpt-oss-20b:free", ...},
        timeout=10
    )
except RequestException as e:
    # Fallback to basic string matching
    return fuzzy_match(name1, name2)
```

---

## Data Models

### Customer Profile
```python
{
    "id": "CUST001",
    "name": "Rajesh Kumar",
    "age": 32,
    "city": "Mumbai",
    "phone": "9876543210",
    "email": "rajesh.kumar@email.com",
    "credit_score": 780,
    "monthly_salary": 85000,
    "current_loans": 1,
    "pre_approved_limit": 300000,
    "kyc_status": "verified",
    "address": "Andheri West, Mumbai"
}
```

### Loan Application
```python
{
    "customer_id": "CUST001",
    "phone": "9876543210",
    "requested_amount": 300000,
    "requested_tenure": 24,
    "interest_rate": 11.5,
    "emi": 13912.81,
    "decision": "approved",
    "decision_reason": "Within pre-approved limit",
    "reason_code": "PRE_APPROVED",
    "salary_slip_uploaded": false,
    "sanction_id": "SAN20241204ABC123",
    "sanction_letter_url": "/api/sanction/download/..."
}
```

### Conversation Memory
```python
{
    "session_id": "uuid-string",
    "phone": "9876543210",
    "customer": {...},
    "application": {...},
    "current_stage": "decision",
    "conversation_history": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ],
    "context": {
        "kyc_verified": true,
        "offer_presented": true,
        "decision": "approved"
    }
}
```

---

## EMI Calculation Formula

```
EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)

Where:
P = Principal loan amount
r = Monthly interest rate (annual_rate / 12 / 100)
n = Tenure in months

Example:
P = ₹300,000
Annual Rate = 11.5%
r = 11.5 / 12 / 100 = 0.00958333
n = 24 months

EMI = 300000 × 0.00958333 × (1.00958333)^24 / ((1.00958333)^24 - 1)
    = ₹13,912.81
```

---

## Interest Rate Matrix

| Credit Score | Category  | Annual Rate |
|--------------|-----------|-------------|
| 800+         | Excellent | 10.5%       |
| 750-799      | Good      | 11.5%       |
| 700-749      | Fair      | 12.5%       |
| < 700        | Below     | Rejected    |

---

## API Request/Response Examples

### Start Chat Session
```http
POST /api/chat/start
Response:
{
    "session_id": "uuid",
    "message": "🙏 **Welcome to Tata Capital!**\n\nHello! I'm your personal loan assistant...\n\n**To get started, please enter your 10-digit mobile number (e.g., 9876543210):**",
    "stage": "intent_capture"
}
```

**Note**: The greeting and phone number request are combined in a single message to avoid duplication.

### Send Message
```http
POST /api/chat
{
    "session_id": "uuid",
    "message": "9876543210"
}

Response:
{
    "session_id": "uuid",
    "message": "Welcome back, Rajesh Kumar!...",
    "stage": "offer_presentation",
    "requires_input": true,
    "input_type": "text"
}
```

### Upload Salary Slip
```http
POST /api/upload?session_id=uuid
Content-Type: multipart/form-data
file: salary.pdf

Response (Success):
{
    "success": true,
    "message": "Salary verified...",
    "parsed_salary": 85000,
    "stage": "decision",
    "metadata": {...}
}

Response (Name Mismatch):
{
    "success": false,
    "message": "❌ **Name Verification Failed**\n\nThe name on the salary slip doesn't match...",
    "name_mismatch": true,
    "customer_name": "Rajesh Kumar",
    "salary_slip_name": "R. K. Sharma"
}
```

### Download Sanction Letter
```http
GET /api/sanction/download/SAN20241204ABC123
Response: PDF file
```

### Generate/Retrieve Sanction Letter
```http
GET /api/sanction/generate/{session_id}
Response: PDF file (streaming)
Headers:
  Content-Disposition: attachment; filename=sanction_{id}.pdf
  Access-Control-Expose-Headers: Content-Disposition
```

---

## Security Considerations (Production)

### Authentication
- JWT tokens for session management
- OAuth 2.0 for third-party integrations
- Multi-factor authentication for sensitive operations

### Data Protection
- Encrypt sensitive data at rest (AES-256)
- Use TLS 1.3 for data in transit
- Implement PII masking in logs
- GDPR compliance for data handling

### API Security
- Rate limiting (100 requests/minute per IP)
- CORS configuration for allowed origins
- Input validation and sanitization
- SQL injection prevention (using ORMs)
- XSS protection

### File Upload Security
- Virus scanning for uploaded files
- File type validation (magic number check)
- Size limits enforcement
- Sandboxed file processing
- Secure file storage with access controls

---

## Performance Optimization

### Backend
- Async/await for I/O operations
- Connection pooling for databases
- Caching frequently accessed data (Redis)
- Background tasks for PDF generation
- Load balancing across multiple instances

### Frontend
- Code splitting and lazy loading
- Image optimization and lazy loading
- Debouncing user inputs
- Virtual scrolling for long conversations
- Service worker for offline capability

### Database (Production)
- Indexing on frequently queried fields
- Query optimization
- Read replicas for scaling
- Partitioning large tables
- Regular vacuum and analyze

---

## Monitoring & Observability

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Correlation IDs for request tracing
- Sensitive data redaction

### Metrics
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Active sessions count
- File upload success rate
- PDF generation time

### Alerts
- High error rate (> 5%)
- Slow response time (> 2s)
- High memory usage (> 80%)
- Disk space low (< 20%)
- Service unavailability

---

## Deployment Architecture (Production)

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
│                  (AWS ALB / Nginx)                      │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐       ┌─────────┐
│Frontend │       │Frontend │
│ Server  │       │ Server  │
│ (Nginx) │       │ (Nginx) │
└─────────┘       └─────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  API Gateway    │
             │  (Kong/AWS)     │
             └────────┬────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
    ┌─────────┐              ┌─────────┐
    │Backend  │              │Backend  │
    │Instance │              │Instance │
    │(FastAPI)│              │(FastAPI)│
    └────┬────┘              └────┬────┘
         │                         │
         └────────────┬────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
    ┌─────────┐              ┌─────────┐
    │  Redis  │              │PostgreSQL│
    │ (Cache) │              │   (DB)   │
    └─────────┘              └─────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   AWS S3      │
              │ (File Storage)│
              └───────────────┘
```

---

## Technology Stack Summary

| Layer          | Technology              | Purpose                    |
|----------------|-------------------------|----------------------------|
| Frontend       | React 18                | UI library                 |
| Build Tool     | Vite 5                  | Fast development & build   |
| HTTP Client    | Axios                   | API communication          |
| Styling        | Custom CSS              | Design system              |
| Backend        | Python 3.11             | Programming language       |
| Web Framework  | FastAPI 0.104           | REST API                   |
| Validation     | Pydantic 2.5            | Data validation            |
| ASGI Server    | Uvicorn 0.24            | Production server          |
| PDF Generation | ReportLab 4.0           | Sanction letters           |
| AI Verification| OpenRouter API          | Name matching verification |
| AI Model       | openai/gpt-oss-20b:free | Name comparison logic      |
| Mock Data      | JSON files              | Customer profiles          |
| Session Store  | In-memory (MVP)         | Conversation state         |
| File Storage   | Local filesystem (MVP)  | Uploads & sanctions        |

---

## Recent Improvements & Bug Fixes

### 1. Initial Session Flow Optimization (Dec 2025)
**Issue**: Mobile number was being requested twice on application start

**Root Cause**: 
- App.jsx called `/api/chat/start`
- ChatInterface.jsx also sent a duplicate "start" message
- This caused the phone number to be requested twice

**Solution**:
- Combined greeting and phone request in a single message
- App.jsx now captures and passes initial message to ChatInterface
- Removed duplicate message sending from ChatInterface
- Result: Clean, single prompt for phone number

### 2. Name Verification Enhancement (Dec 2025)
**Feature**: AI-powered name matching between CRM and salary slip

**Implementation**:
- Integrated OpenRouter API for intelligent name comparison
- Model: `openai/gpt-oss-20b:free`
- Handles name variations, nicknames, and different formats
- Returns detailed reasoning for mismatches
- Provides confidence scores

**Security**: Prevents fraudulent salary slip uploads by verifying name consistency

### 3. Mock Data Structure (Dec 2025)
**File**: `mock_data.json` in project root

**Structure**:
```json
{
  "customers": [
    {
      "id": "CUST001",
      "name": "Rajesh Kumar",
      "age": 32,
      "city": "Mumbai",
      "phone": "9876543210",
      "email": "rajesh.kumar@example.com",
      "credit_score": 780,
      "monthly_salary": 85000,
      "current_loans": 1,
      "pre_approved_limit": 300000,
      "kyc_status": "verified",
      "address": "123, Marine Drive, Mumbai, Maharashtra - 400001"
    }
  ]
}
```

**Contains**: 10 diverse customer profiles for testing various scenarios:
- Instant approval (high credit, within limit)
- Conditional approval (requires salary slip)
- Rejection scenarios (low credit, high EMI ratio)
- Different credit scores (580-840)
- Various salary ranges (₹42,000 - ₹1,35,000)

### 4. Sanction Letter Generation
**File Storage**: `data/sanction_letters/` directory

**Features**:
- Professional PDF generation with company branding
- Unique sanction IDs
- Comprehensive loan terms and conditions
- Download via streaming response
- Caching for repeat downloads
- Currency format: Rs. (instead of ₹ for PDF compatibility)

---

## Environment Configuration

### Required Environment Variables
Create a `.env` file in the project root:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenRouter API (for name verification)
OPENROUTER_API_KEY=your_api_key_here

# File Paths
UPLOAD_DIR=./uploads
SANCTION_DIR=./data/sanction_letters
```

---

## Conclusion

This architecture provides a **scalable, maintainable, and production-ready** foundation for an NBFC loan processing system powered by multi-agent AI.

The modular design allows for:
- Easy addition of new agents
- Flexible business rule modifications
- Seamless integration with real APIs
- Horizontal scaling capabilities
- Comprehensive monitoring and debugging
- **AI-powered fraud prevention** through name verification
- **Optimized user experience** with streamlined conversation flow

**Status**: ✅ **Fully Functional MVP with Enhanced Security**

**Key Features**:
- ✅ Multi-agent architecture
- ✅ Complete loan workflow (greeting → approval → sanction)
- ✅ AI-powered name verification
- ✅ Professional PDF sanction letters
- ✅ Salary slip parsing and validation
- ✅ Business rule-based underwriting
- ✅ Premium UI/UX with glassmorphism
- ✅ File upload with validation
- ✅ Session management
- ✅ Error handling and edge cases
