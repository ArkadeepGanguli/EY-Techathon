"""State Machine for conversation flow management"""

from models import ConversationStage, ConversationMemory, LoanDecision
from typing import Optional


class StateMachine:
    """
    State machine to manage conversation flow transitions
    
    Stages:
    1. GREETING
    2. INTENT_CAPTURE
    3. LEAD_QUALIFICATION
    4. OFFER_PRESENTATION
    5. KYC_VERIFICATION
    6. UNDERWRITING
    7. DECISION
    8. SANCTION_LETTER (if approved)
    9. CLOSE
    """
    
    # Define valid transitions
    TRANSITIONS = {
        ConversationStage.GREETING: [ConversationStage.INTENT_CAPTURE],
        ConversationStage.INTENT_CAPTURE: [ConversationStage.LEAD_QUALIFICATION],
        ConversationStage.LEAD_QUALIFICATION: [ConversationStage.OFFER_PRESENTATION, ConversationStage.CLOSE],
        ConversationStage.OFFER_PRESENTATION: [ConversationStage.KYC_VERIFICATION, ConversationStage.OFFER_PRESENTATION],  # Can loop for tenure changes
        ConversationStage.KYC_VERIFICATION: [ConversationStage.UNDERWRITING, ConversationStage.KYC_VERIFICATION],  # Can loop for OTP
        ConversationStage.UNDERWRITING: [ConversationStage.DECISION, ConversationStage.KYC_VERIFICATION],  # Can go back for salary slip
        ConversationStage.DECISION: [ConversationStage.SANCTION_LETTER, ConversationStage.CLOSE],
        ConversationStage.SANCTION_LETTER: [ConversationStage.CLOSE],
        ConversationStage.CLOSE: []  # Terminal state
    }
    
    def __init__(self):
        """Initialize state machine"""
        pass
    
    def can_transition(self, current_stage: ConversationStage, 
                      next_stage: ConversationStage) -> bool:
        """
        Check if transition is valid
        
        Args:
            current_stage: Current conversation stage
            next_stage: Desired next stage
            
        Returns:
            True if transition is valid, False otherwise
        """
        valid_next_stages = self.TRANSITIONS.get(current_stage, [])
        return next_stage in valid_next_stages
    
    def transition(self, memory: ConversationMemory, 
                  next_stage: ConversationStage) -> bool:
        """
        Transition to next stage
        
        Args:
            memory: Conversation memory
            next_stage: Desired next stage
            
        Returns:
            True if transition successful, False otherwise
        """
        if self.can_transition(memory.current_stage, next_stage):
            memory.current_stage = next_stage
            return True
        return False
    
    def get_next_stage(self, current_stage: ConversationStage, 
                      context: dict) -> ConversationStage:
        """
        Determine next stage based on current stage and context
        
        Args:
            current_stage: Current conversation stage
            context: Context dictionary with additional information
            
        Returns:
            Next conversation stage
        """
        if current_stage == ConversationStage.GREETING:
            return ConversationStage.INTENT_CAPTURE
        
        elif current_stage == ConversationStage.INTENT_CAPTURE:
            return ConversationStage.LEAD_QUALIFICATION
        
        elif current_stage == ConversationStage.LEAD_QUALIFICATION:
            # Check if customer found
            if context.get('customer_found'):
                return ConversationStage.OFFER_PRESENTATION
            else:
                return ConversationStage.CLOSE
        
        elif current_stage == ConversationStage.OFFER_PRESENTATION:
            # Check if offer accepted
            if context.get('offer_accepted'):
                return ConversationStage.KYC_VERIFICATION
            else:
                return ConversationStage.OFFER_PRESENTATION  # Stay for negotiation
        
        elif current_stage == ConversationStage.KYC_VERIFICATION:
            # Check if KYC verified
            if context.get('kyc_verified'):
                return ConversationStage.UNDERWRITING
            else:
                return ConversationStage.KYC_VERIFICATION  # Stay for OTP/verification
        
        elif current_stage == ConversationStage.UNDERWRITING:
            # Check decision
            decision = context.get('decision')
            if decision == LoanDecision.CONDITIONAL:
                return ConversationStage.KYC_VERIFICATION  # Go back for salary slip
            else:
                return ConversationStage.DECISION
        
        elif current_stage == ConversationStage.DECISION:
            # Check if approved
            decision = context.get('decision')
            if decision == LoanDecision.APPROVED:
                return ConversationStage.SANCTION_LETTER
            else:
                return ConversationStage.CLOSE
        
        elif current_stage == ConversationStage.SANCTION_LETTER:
            return ConversationStage.CLOSE
        
        else:  # CLOSE or unknown
            return ConversationStage.CLOSE


# Singleton instance
state_machine = StateMachine()
