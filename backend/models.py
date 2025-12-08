"""Data models for the NBFC Loan System"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class ConversationStage(str, Enum):
    """Stages in the loan conversation flow"""
    GREETING = "greeting"
    INTENT_CAPTURE = "intent_capture"
    LEAD_QUALIFICATION = "lead_qualification"
    OFFER_PRESENTATION = "offer_presentation"
    KYC_VERIFICATION = "kyc_verification"
    UNDERWRITING = "underwriting"
    DECISION = "decision"
    SANCTION_LETTER = "sanction_letter"
    CLOSE = "close"


class LoanDecision(str, Enum):
    """Possible loan decisions"""
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"  # Requires salary slip
    PENDING = "pending"


class Customer(BaseModel):
    """Customer profile from CRM"""
    id: str
    name: str
    age: int
    city: str
    phone: str
    email: str
    credit_score: int
    monthly_salary: float
    current_loans: int
    pre_approved_limit: float
    kyc_status: Literal["verified", "pending", "failed"]
    address: str


class LoanApplication(BaseModel):
    """Loan application state"""
    application_id: Optional[str] = None
    customer_id: Optional[str] = None
    phone: str
    requested_amount: Optional[float] = None
    requested_tenure: Optional[int] = None
    approved_amount: Optional[float] = None
    approved_tenure: Optional[int] = None
    tenure: Optional[int] = None  # Alias for approved_tenure
    interest_rate: Optional[float] = None
    emi: Optional[float] = None
    emi_amount: Optional[float] = None  # Alias for emi
    loan_approved: bool = False
    decision: LoanDecision = LoanDecision.PENDING
    decision_reason: Optional[str] = None
    reason_code: Optional[str] = None
    salary_slip_uploaded: bool = False
    salary_slip_url: Optional[str] = None
    parsed_salary: Optional[float] = None
    sanction_id: Optional[str] = None
    sanction_letter_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ConversationMemory(BaseModel):
    """Conversation state and memory"""
    session_id: str
    phone: Optional[str] = None
    customer: Optional[Customer] = None
    application: Optional[LoanApplication] = None
    current_stage: ConversationStage = ConversationStage.GREETING
    conversation_history: List[dict] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class ChatMessage(BaseModel):
    """Chat message from user"""
    session_id: str
    message: str
    phone: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from the chatbot"""
    session_id: str
    message: str
    stage: ConversationStage
    requires_input: bool = True
    input_type: Optional[Literal["text", "file", "choice"]] = "text"
    choices: Optional[List[str]] = None
    metadata: Optional[dict] = None


class OfferDetails(BaseModel):
    """Loan offer details"""
    amount: float
    tenure: int
    interest_rate: float
    emi: float
    total_payable: float


class SanctionRequest(BaseModel):
    """Request to generate sanction letter"""
    customer: Customer
    application: LoanApplication
    offer: OfferDetails


class SanctionResponse(BaseModel):
    """Sanction letter generation response"""
    sanction_id: str
    pdf_url: str
    generated_at: datetime
