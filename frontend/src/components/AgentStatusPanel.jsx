import React, { useRef, useEffect } from 'react';
import './AgentStatusPanel.css';

const AgentStatusPanel = ({ currentStage, application, sanctionData }) => {
    const approvalCardRef = useRef(null);

    // Auto-scroll to approval card when it appears
    useEffect(() => {
        if ((currentStage === 'sanction_letter' || currentStage === 'close') && application?.loan_approved && approvalCardRef.current) {
            approvalCardRef.current.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }
    }, [currentStage, application?.loan_approved]);
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

    const agents = [
        {
            id: 1,
            name: 'Master Agent',
            desc: 'Orchestrating Workflow',
            stage: 'greeting',
            icon: '🎯'
        },
        {
            id: 2,
            name: 'Sales Agent',
            desc: 'Processing Offer',
            stage: 'offer_presentation',
            icon: '💼'
        },
        {
            id: 3,
            name: 'Verification Agent',
            desc: 'KYC Verification',
            stage: 'kyc_verification',
            icon: '🔍'
        },
        {
            id: 4,
            name: 'Underwriting Agent',
            desc: 'Risk Assessment',
            stage: 'underwriting',
            icon: '📊'
        },
        {
            id: 5,
            name: 'Sanction Agent',
            desc: 'Letter Generation',
            stage: 'sanction_letter',
            icon: '📄'
        }
    ];

    return (
        <div className="agent-status-panel">
            <div className="panel-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                <h2 className="panel-title">Agent Status</h2>
            </div>

            <div className="agents-list">
                {agents.map(agent => (
                    <AgentCard
                        key={agent.id}
                        name={agent.name}
                        desc={agent.desc}
                        icon={agent.icon}
                        status={getAgentStatus(agent.stage)}
                    />
                ))}
            </div>

            {/* Approval Card */}
            {(currentStage === 'sanction_letter' || currentStage === 'close') && application?.loan_approved && (
                <div ref={approvalCardRef} className="approval-banner">
                    <div className="approval-icon">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="#4caf50">
                            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                        </svg>
                    </div>
                    <div className="approval-content">
                        <h3>🎉 Loan Approved!</h3>
                        <p>Your sanction letter is ready</p>
                        {sanctionData && (
                            <a
                                href={`/api/sanction/generate/${sanctionData.session_id}`}
                                download={`sanction_${sanctionData.sanction_id}.pdf`}
                                className="download-btn"
                            >
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2z" />
                                </svg>
                                Download PDF
                            </a>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

const AgentCard = ({ name, desc, icon, status }) => (
    <div className={`agent-card ${status}`}>
        <div className="agent-icon">{icon}</div>
        <div className="agent-info">
            <div className="agent-name">{name}</div>
            <div className="agent-desc">{desc}</div>
        </div>
        <div className={`status-badge ${status}`}>
            {status === 'active' && <span className="pulse-dot"></span>}
            {status === 'completed' && '✓'}
            {status === 'pending' && '○'}
        </div>
    </div>
);

export default AgentStatusPanel;
