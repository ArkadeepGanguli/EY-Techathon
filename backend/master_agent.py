"""Master Agent - The Orchestrator"""

from models import (ConversationStage, ConversationMemory, ChatMessage, ChatResponse,
                   LoanApplication, LoanDecision, OfferDetails, Customer)
from memory_manager import memory_manager
from state_machine import state_machine
from agents import sales_agent, verification_agent, underwriting_agent, sanction_agent
from mocks import crm_service, credit_bureau_service
from typing import Optional
import re


class MasterAgent:
    """
    Master Agent (Orchestrator) responsible for:
    - Greeting users
    - Collecting intent, amount, tenure
    - Fetching CRM profile
    - Delegating tasks to Worker Agents
    - Keeping unified conversation memory
    - Deciding workflow transitions
    - Handling special cases (errors, rejections, escalations)
    - Summarizing decisions & generating final response
    """
    
    def __init__(self):
        """Initialize master agent"""
        self.memory_manager = memory_manager
        self.state_machine = state_machine
    
    def process_message(self, message: ChatMessage) -> ChatResponse:
        """
        Main entry point - process user message and orchestrate response
        
        Args:
            message: User's chat message
            
        Returns:
            ChatResponse with agent's reply
        """
        # Get or create session
        memory = self.memory_manager.get_session(message.session_id)
        if not memory:
            session_id = self.memory_manager.create_session()
            memory = self.memory_manager.get_session(session_id)
            message.session_id = session_id
        
        # Add user message to history
        self.memory_manager.add_message(message.session_id, "user", message.message)
        
        # Process based on current stage
        current_stage = memory.current_stage
        
        if current_stage == ConversationStage.GREETING:
            response = self._handle_greeting(message, memory)
        
        elif current_stage == ConversationStage.INTENT_CAPTURE:
            response = self._handle_intent_capture(message, memory)
        
        elif current_stage == ConversationStage.LEAD_QUALIFICATION:
            response = self._handle_lead_qualification(message, memory)
        
        elif current_stage == ConversationStage.OFFER_PRESENTATION:
            response = self._handle_offer_presentation(message, memory)
        
        elif current_stage == ConversationStage.KYC_VERIFICATION:
            response = self._handle_kyc_verification(message, memory)
        
        elif current_stage == ConversationStage.UNDERWRITING:
            response = self._handle_underwriting(message, memory)
        
        elif current_stage == ConversationStage.DECISION:
            response = self._handle_decision(message, memory)
        
        elif current_stage == ConversationStage.SANCTION_LETTER:
            response = self._handle_sanction_letter(message, memory)
        
        elif current_stage == ConversationStage.CLOSE:
            response = self._handle_close(message, memory)
        
        else:
            response = ChatResponse(
                session_id=message.session_id,
                message="I'm sorry, something went wrong. Let's start over.",
                stage=ConversationStage.GREETING
            )
        
        # Add assistant message to history
        self.memory_manager.add_message(message.session_id, "assistant", response.message)
        
        return response
    
    def _handle_greeting(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle greeting stage"""
        
        greeting_message = """
🙏 **Welcome to Tata Capital!**

Hello! I'm your personal loan assistant. I'm here to help you get a personal loan quickly and easily.

**Here's how I can help you:**
✅ Check your pre-approved loan offers
✅ Provide instant loan approval
✅ Calculate EMI options
✅ Generate sanction letter

**To get started, please enter your 10-digit mobile number (e.g., 9876543210):**
""".strip()
        
        # Transition to intent capture
        self.state_machine.transition(memory, ConversationStage.INTENT_CAPTURE)
        self.memory_manager.update_session(message.session_id, memory)
        
        return ChatResponse(
            session_id=message.session_id,
            message=greeting_message,
            stage=ConversationStage.INTENT_CAPTURE,
            requires_input=True,
            input_type="text"
        )
    
    def _handle_intent_capture(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle intent capture - get phone number"""
        
        # Extract phone number from message
        phone = self._extract_phone(message.message)
        
        if not phone:
            return ChatResponse(
                session_id=message.session_id,
                message="Please enter a valid 10-digit mobile number (e.g., 9876543210):",
                stage=ConversationStage.INTENT_CAPTURE,
                requires_input=True,
                input_type="text"
            )
        
        # Store phone and transition
        memory.phone = phone
        self.memory_manager.update_context(message.session_id, 'phone', phone)
        self.state_machine.transition(memory, ConversationStage.LEAD_QUALIFICATION)
        self.memory_manager.update_session(message.session_id, memory)
        
        # Immediately process lead qualification
        return self._fetch_customer_and_qualify(message.session_id, phone, memory)
    
    def _handle_lead_qualification(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle lead qualification - should not reach here normally"""
        return self._fetch_customer_and_qualify(message.session_id, memory.phone, memory)
    
    def _fetch_customer_and_qualify(self, session_id: str, phone: str, 
                                   memory: ConversationMemory) -> ChatResponse:
        """Fetch customer from CRM and qualify lead"""
        
        # Fetch customer from CRM
        customer = crm_service.get_customer_by_phone(phone)
        
        if not customer:
            # Customer not found
            not_found_message = f"""
😔 **Customer Not Found**

I couldn't find an account with phone number {phone}.

**To apply for a loan, you can:**
• Visit our website: www.tatacapital.com
• Call us: 1800-123-4567
• Visit nearest branch

Thank you for your interest!
""".strip()
            
            self.state_machine.transition(memory, ConversationStage.CLOSE)
            self.memory_manager.update_session(session_id, memory)
            
            return ChatResponse(
                session_id=session_id,
                message=not_found_message,
                stage=ConversationStage.CLOSE,
                requires_input=False
            )
        
        # Customer found - store in memory
        self.memory_manager.set_customer(session_id, customer)
        
        # Create loan application
        application = LoanApplication(phone=phone, customer_id=customer.id)
        self.memory_manager.set_application(session_id, application)
        
        # Ask for loan details
        qualification_message = f"""
✅ **Welcome back, {customer.name}!**

Great news! You have a **pre-approved loan offer** of up to **₹{customer.pre_approved_limit:,.0f}**!

**To help you better, I need to know:**

1️⃣ **How much loan amount do you need?** (in ₹)
2️⃣ **What tenure would you prefer?** (12, 24, 36, 48, or 60 months)

Please tell me the amount and tenure. For example: "I need 200000 for 24 months" or "3 lakhs for 3 years"
""".strip()
        
        self.state_machine.transition(memory, ConversationStage.OFFER_PRESENTATION)
        self.memory_manager.update_session(session_id, memory)
        
        return ChatResponse(
            session_id=session_id,
            message=qualification_message,
            stage=ConversationStage.OFFER_PRESENTATION,
            requires_input=True,
            input_type="text"
        )
    
    def _handle_offer_presentation(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle offer presentation stage"""
        
        customer = memory.customer
        application = memory.application
        
        # Check if offer was already presented and user is responding
        if self.memory_manager.get_context(message.session_id, 'offer_presented'):
            user_response = message.message.lower().strip()
            
            # Check if user accepts the offer
            if user_response in ['yes', 'y', 'ok', 'proceed', 'accept', 'sure']:
                # User accepted - move to KYC verification
                self.state_machine.transition(memory, ConversationStage.KYC_VERIFICATION)
                self.memory_manager.update_session(message.session_id, memory)
                
                # Process KYC verification
                return self._handle_kyc_verification(message, memory)
            
            # Check if user wants to change tenure
            elif 'change' in user_response or 'modify' in user_response or 'different' in user_response:
                # Reset offer presented flag
                self.memory_manager.update_context(message.session_id, 'offer_presented', False)
                return ChatResponse(
                    session_id=message.session_id,
                    message="Sure! Please tell me the new tenure you'd like (12, 24, 36, 48, or 60 months):",
                    stage=ConversationStage.OFFER_PRESENTATION,
                    requires_input=True,
                    input_type="text"
                )
            else:
                # Unclear response
                return ChatResponse(
                    session_id=message.session_id,
                    message="Please type 'yes' to proceed with this offer or 'change tenure' to modify it.",
                    stage=ConversationStage.OFFER_PRESENTATION,
                    requires_input=True,
                    input_type="text"
                )
        
        # Check if we already have amount and tenure
        if not application.requested_amount or not application.requested_tenure:
            # Extract amount and tenure from message
            amount = self._extract_amount(message.message)
            tenure = self._extract_tenure(message.message)
            
            if not amount:
                return ChatResponse(
                    session_id=message.session_id,
                    message="Please specify the loan amount you need. For example: '200000' or '2 lakhs'",
                    stage=ConversationStage.OFFER_PRESENTATION,
                    requires_input=True,
                    input_type="text"
                )
            
            if not tenure:
                return ChatResponse(
                    session_id=message.session_id,
                    message="Please specify the tenure in months (12, 24, 36, 48, or 60). For example: '24 months' or '2 years'",
                    stage=ConversationStage.OFFER_PRESENTATION,
                    requires_input=True,
                    input_type="text"
                )
            
            # Store in application
            application.requested_amount = amount
            application.requested_tenure = tenure
            self.memory_manager.set_application(message.session_id, application)
        
        # Present offer using Sales Agent
        offer_result = sales_agent.present_offer(customer, application.requested_amount, 
                                                 application.requested_tenure)
        
        # Store interest rate and EMI
        application.interest_rate = offer_result['offer'].interest_rate
        application.emi = offer_result['offer'].emi
        self.memory_manager.set_application(message.session_id, application)
        
        # Ask for confirmation
        confirmation_message = offer_result['message'] + "\n\n**Type 'yes' to proceed or 'change tenure' to modify.**"
        
        self.memory_manager.update_context(message.session_id, 'offer_presented', True)
        self.memory_manager.update_context(message.session_id, 'current_offer', offer_result['offer'])
        
        return ChatResponse(
            session_id=message.session_id,
            message=confirmation_message,
            stage=ConversationStage.OFFER_PRESENTATION,
            requires_input=True,
            input_type="text"
        )
    
    def _handle_kyc_verification(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle KYC verification stage"""
        
        customer = memory.customer
        
        # Check if we need to verify KYC
        if not self.memory_manager.get_context(message.session_id, 'kyc_checked'):
            # First time - check KYC status
            kyc_result = verification_agent.verify_kyc(customer)
            self.memory_manager.update_context(message.session_id, 'kyc_checked', True)
            
            if kyc_result['verified']:
                # KYC already verified - move to underwriting
                self.memory_manager.update_context(message.session_id, 'kyc_verified', True)
                self.state_machine.transition(memory, ConversationStage.UNDERWRITING)
                self.memory_manager.update_session(message.session_id, memory)
                
                # Immediately process underwriting
                return self._process_underwriting(message.session_id, memory)
            
            elif kyc_result.get('requires_otp'):
                # Need OTP verification
                return ChatResponse(
                    session_id=message.session_id,
                    message=kyc_result['message'],
                    stage=ConversationStage.KYC_VERIFICATION,
                    requires_input=True,
                    input_type="text"
                )
            
            else:
                # KYC failed
                self.state_machine.transition(memory, ConversationStage.CLOSE)
                self.memory_manager.update_session(message.session_id, memory)
                
                return ChatResponse(
                    session_id=message.session_id,
                    message=kyc_result['message'],
                    stage=ConversationStage.CLOSE,
                    requires_input=False
                )
        
        # Handle OTP verification or salary slip upload
        if self.memory_manager.get_context(message.session_id, 'awaiting_salary_slip'):
            # Check if user wants to cancel
            user_input = message.message.lower().strip()
            if user_input in ['cancel', 'cancel application', 'stop', 'quit', 'exit']:
                # User wants to cancel
                self.state_machine.transition(memory, ConversationStage.CLOSE)
                self.memory_manager.update_session(message.session_id, memory)
                
                return ChatResponse(
                    session_id=message.session_id,
                    message="""
🚫 **Application Cancelled**

Your loan application has been cancelled as requested.

Thank you for your interest in Tata Capital. You can start a new application anytime by refreshing the page.

If you have any questions, please contact us at:
📞 1800-123-4567
📧 support@tatacapital.com

Have a great day! 🙏
""".strip(),
                    stage=ConversationStage.CLOSE,
                    requires_input=False
                )
            
            # Otherwise, prompt for file upload
            return ChatResponse(
                session_id=message.session_id,
                message="Please upload your salary slip using the file upload button above, or type 'cancel' to cancel the application.",
                stage=ConversationStage.KYC_VERIFICATION,
                requires_input=True,
                input_type="file"
            )
        
        else:
            # Simulate OTP verification (any response verifies)
            otp_result = verification_agent.simulate_otp_verification(customer)
            self.memory_manager.update_context(message.session_id, 'kyc_verified', True)
            
            # Move to underwriting
            self.state_machine.transition(memory, ConversationStage.UNDERWRITING)
            self.memory_manager.update_session(message.session_id, memory)
            
            # Process underwriting
            return self._process_underwriting(message.session_id, memory)
    
    def _handle_underwriting(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle underwriting stage"""
        return self._process_underwriting(message.session_id, memory)
    
    def _process_underwriting(self, session_id: str, memory: ConversationMemory) -> ChatResponse:
        """Process underwriting evaluation"""
        
        customer = memory.customer
        application = memory.application
        
        # Get parsed salary if available
        parsed_salary = application.parsed_salary if application.salary_slip_uploaded else None
        
        # Evaluate loan using Underwriting Agent
        evaluation = underwriting_agent.evaluate_loan(
            customer, 
            application.requested_amount,
            application.requested_tenure,
            parsed_salary
        )
        
        # Store decision
        application.decision = evaluation['decision']
        application.decision_reason = evaluation['reason']
        application.reason_code = evaluation['reason_code']
        
        # If approved, set approved fields
        if evaluation['decision'] == LoanDecision.APPROVED:
            application.loan_approved = True
            application.approved_amount = application.requested_amount
            application.approved_tenure = application.requested_tenure
            application.tenure = application.requested_tenure
            application.emi_amount = application.emi
            # Generate application ID if not present
            if not application.application_id:
                application.application_id = session_id[:8].upper()
        
        self.memory_manager.set_application(session_id, application)
        
        # Handle decision
        if evaluation['decision'] == LoanDecision.CONDITIONAL:
            # Need salary slip
            self.memory_manager.update_context(session_id, 'awaiting_salary_slip', True)
            
            salary_request = verification_agent.request_salary_slip(customer, evaluation['reason'])
            
            return ChatResponse(
                session_id=session_id,
                message=evaluation['message'] + "\n\n" + salary_request,
                stage=ConversationStage.KYC_VERIFICATION,
                requires_input=True,
                input_type="file"
            )
        
        else:
            # Move to decision stage
            self.memory_manager.update_context(session_id, 'decision', evaluation['decision'])
            
            # If approved, automatically generate sanction letter
            if evaluation['decision'] == LoanDecision.APPROVED:
                self.state_machine.transition(memory, ConversationStage.SANCTION_LETTER)
                self.memory_manager.update_session(session_id, memory)
                
                # Generate sanction letter immediately
                return self._generate_sanction_letter(session_id, memory)
            else:
                # Rejected - move to close
                self.state_machine.transition(memory, ConversationStage.CLOSE)
                self.memory_manager.update_session(session_id, memory)
                
                return ChatResponse(
                    session_id=session_id,
                    message=evaluation['message'],
                    stage=ConversationStage.CLOSE,
                    requires_input=False
                )
    
    def _handle_decision(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle decision stage"""
        
        application = memory.application
        
        if application.decision == LoanDecision.APPROVED:
            # Move to sanction letter generation
            self.state_machine.transition(memory, ConversationStage.SANCTION_LETTER)
            self.memory_manager.update_session(message.session_id, memory)
            
            return self._generate_sanction_letter(message.session_id, memory)
        
        else:
            # Rejected - close conversation
            self.state_machine.transition(memory, ConversationStage.CLOSE)
            self.memory_manager.update_session(message.session_id, memory)
            
            return ChatResponse(
                session_id=message.session_id,
                message="Thank you for your interest. Is there anything else I can help you with?",
                stage=ConversationStage.CLOSE,
                requires_input=False
            )
    
    def _handle_sanction_letter(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle sanction letter generation"""
        return self._generate_sanction_letter(message.session_id, memory)
    
    def _generate_sanction_letter(self, session_id: str, memory: ConversationMemory) -> ChatResponse:
        """Generate sanction letter"""
        
        customer = memory.customer
        application = memory.application
        
        # Create offer details
        offer = OfferDetails(
            amount=application.requested_amount,
            tenure=application.requested_tenure,
            interest_rate=application.interest_rate,
            emi=application.emi,
            total_payable=application.emi * application.requested_tenure
        )
        
        # Generate sanction letter using Sanction Agent
        sanction_response = sanction_agent.generate_sanction_letter(customer, application, offer)
        
        # Update application
        application.sanction_id = sanction_response.sanction_id
        application.sanction_letter_url = sanction_response.pdf_url
        self.memory_manager.set_application(session_id, application)
        
        # Craft message
        sanction_message = sanction_agent.craft_sanction_message(
            customer, 
            sanction_response.sanction_id,
            sanction_response.pdf_url,
            offer
        )
        
        # Move to close
        self.state_machine.transition(memory, ConversationStage.CLOSE)
        self.memory_manager.update_session(session_id, memory)
        
        return ChatResponse(
            session_id=session_id,
            message=sanction_message,
            stage=ConversationStage.CLOSE,
            requires_input=False,
            metadata={
                "sanction_id": sanction_response.sanction_id,
                "pdf_url": sanction_response.pdf_url
            }
        )
    
    def _handle_close(self, message: ChatMessage, memory: ConversationMemory) -> ChatResponse:
        """Handle close stage"""
        
        return ChatResponse(
            session_id=message.session_id,
            message="Thank you for choosing Tata Capital! Have a great day! 🙏",
            stage=ConversationStage.CLOSE,
            requires_input=False
        )
    
    # Helper methods for extraction
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract 10-digit phone number from text"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', text)
        
        # Check if we have exactly 10 digits or 10 digits after country code
        if len(digits) == 10:
            return digits
        elif len(digits) == 12 and digits.startswith('91'):
            return digits[2:]
        
        return None
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract loan amount from text"""
        text = text.lower()
        
        # Look for patterns like "2 lakhs", "200000", "2L", "2 lakh"
        lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)\b', text)
        if lakh_match:
            return float(lakh_match.group(1)) * 100000
        
        # Look for plain numbers
        number_match = re.search(r'\b(\d{4,})\b', text)
        if number_match:
            return float(number_match.group(1))
        
        return None
    
    def _extract_tenure(self, text: str) -> Optional[int]:
        """Extract tenure from text"""
        text = text.lower()
        
        # Look for patterns like "24 months", "2 years"
        months_match = re.search(r'(\d+)\s*(?:months?|mnths?|mos?)\b', text)
        if months_match:
            return int(months_match.group(1))
        
        years_match = re.search(r'(\d+)\s*(?:years?|yrs?|y)\b', text)
        if years_match:
            return int(years_match.group(1)) * 12
        
        # Look for just numbers in context
        if 'tenure' in text or 'period' in text:
            number_match = re.search(r'\b(\d+)\b', text)
            if number_match:
                num = int(number_match.group(1))
                # Assume months if reasonable
                if num in [12, 24, 36, 48, 60]:
                    return num
        
        return None


# Singleton instance
master_agent = MasterAgent()
