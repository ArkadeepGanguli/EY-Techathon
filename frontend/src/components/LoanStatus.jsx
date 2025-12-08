import React from 'react';
import './LoanStatus.css';

const LoanStatus = ({ application, customer, currentStage, sanctionData }) => {
    // Determine agent statuses based on current stage
    const getAgentStatus = (agentStage) => {
        const stages = [
            'greeting',
            'intent_capture',
            'lead_qualification',
            'offer_presentation',
            'kyc_verification',
            'underwriting',
            'decision',
            'sanction_letter',
            'close'
        ];

        const currentIndex = stages.indexOf(currentStage);
        const agentIndex = stages.indexOf(agentStage);

        if (agentIndex < currentIndex) return 'completed';
        if (agentIndex === currentIndex) return 'active';
        return 'pending';
    };

    const formatCurrency = (amount) => {
        if (!amount) return '₹ 0';
        return `₹ ${amount.toLocaleString('en-IN')}`;
    };

    const loanAmount = application?.requested_amount || application?.approved_amount || 0;
    const tenure = application?.requested_tenure || application?.approved_tenure || 0;
    const interestRate = application?.interest_rate || 0;
    const emi = application?.emi || application?.emi_amount || 0;

    const getProgressPercentage = () => {
        const stages = [
            'greeting',
            'intent_capture',
            'lead_qualification',
            'offer_presentation',
            'kyc_verification',
            'underwriting',
            'decision',
            'sanction_letter',
            'close'
        ];

        const currentIndex = stages.indexOf(currentStage);
        if (currentIndex === -1) return 0;
        return Math.round(((currentIndex + 1) / stages.length) * 100);
    };

    return (
        <div className="loan-status-panel">
            {/* Top Row: Two Cards Side by Side */}
            <div className="status-grid">
                {/* Loan Application Summary */}
                <div className="status-card summary-card">
                    <h3 className="status-card-title">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ marginRight: '0.5rem', verticalAlign: 'middle' }}>
                            <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 16H5V5h2v3h10V5h2v14z" />
                        </svg>
                        Loan Summary
                    </h3>
                    <div className="summary-grid">
                        <div className="summary-item">
                            <span className="summary-label">Amount</span>
                            <span className="summary-value">{formatCurrency(loanAmount)}</span>
                        </div>
                        <div className="summary-item">
                            <span className="summary-label">Tenure</span>
                            <span className="summary-value">{tenure} Mo</span>
                        </div>
                        <div className="summary-item">
                            <span className="summary-label">Rate</span>
                            <span className="summary-value">{interestRate}%</span>
                        </div>
                        <div className="summary-item highlight">
                            <span className="summary-label">Monthly EMI</span>
                            <span className="summary-value-large">{formatCurrency(emi)}</span>
                        </div>
                    </div>
                </div>

                {/* Workflow Progress */}
                <div className="status-card workflow-card">
                    <h3 className="status-card-title">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ marginRight: '0.5rem', verticalAlign: 'middle' }}>
                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                        </svg>
                        AI Workflow
                    </h3>
                    <div className="workflow-progress">
                        {/* Progress Bar */}
                        <div className="progress-bar-container">
                            <div className="progress-bar" style={{ width: `${getProgressPercentage()}%` }}></div>
                        </div>
                        <div className="progress-text">{getProgressPercentage()}% Complete</div>
                    </div>
                </div>
            </div>

            {/* Agent Status List */}
            <div className="status-card agents-card">
                <h3 className="status-card-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style={{ marginRight: '0.5rem', verticalAlign: 'middle' }}>
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                    </svg>
                    Agent Status
                </h3>

                <div className="agents-grid">
                    <AgentStatus
                        name="Master Agent"
                        desc="Orchestrating"
                        status={getAgentStatus('greeting')}
                        icon="MA"
                    />
                    <AgentStatus
                        name="Sales"
                        desc="Offer Terms"
                        status={getAgentStatus('offer_presentation')}
                        icon="💼"
                    />
                    <AgentStatus
                        name="Verification"
                        desc="KYC Check"
                        status={getAgentStatus('kyc_verification')}
                        icon="🔍"
                    />
                    <AgentStatus
                        name="Underwriting"
                        desc="Risk Assessment"
                        status={getAgentStatus('underwriting')}
                        icon="📊"
                    />
                    <AgentStatus
                        name="Sanction"
                        desc="Doc Generation"
                        status={getAgentStatus('sanction_letter')}
                        icon="📄"
                    />
                </div>
            </div>

            {/* Loan Approval Status */}
            {(currentStage === 'sanction_letter' || currentStage === 'close') && application?.loan_approved && (
                <div className="status-card approval-card">
                    <div className="approval-content">
                        <div className="approval-icon-large">
                            <svg width="40" height="40" viewBox="0 0 24 24" fill="#4caf50">
                                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                            </svg>
                        </div>
                        <h3 className="approval-title">🎉 Loan Approved!</h3>
                        <p className="approval-desc">Your sanction letter is ready for download.</p>
                        {sanctionData && (
                            <a
                                href={`/api/sanction/generate/${sanctionData.session_id || application.application_id}`}
                                download={`sanction_letter_${sanctionData.sanction_id}.pdf`}
                                className="download-button-modern"
                            >
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2z" />
                                </svg>
                                Download Sanction Letter
                            </a>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

// Agent Status Component
const AgentStatus = ({ name, desc, status, icon }) => (
    <div className={`agent-item ${status}`}>
        <div className="agent-icon-mini">{icon}</div>
        <div className="agent-info-mini">
            <div className="agent-name-mini">{name}</div>
            <div className="agent-desc-mini">{desc}</div>
        </div>
        <div className={`agent-badge ${status}`}>
            {status === 'active' && '⚡'}
            {status === 'completed' && '✓'}
            {status === 'pending' && '○'}
        </div>
    </div>
);

export default LoanStatus;
