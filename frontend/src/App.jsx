import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import LoanSummaryCard from './components/LoanSummaryCard';
import AgentStatusPanel from './components/AgentStatusPanel';
import './App.css';

function App() {
    const [sessionId, setSessionId] = useState(null);
    const [initialMessage, setInitialMessage] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [customer, setCustomer] = useState(null);
    const [application, setApplication] = useState(null);
    const [currentStage, setCurrentStage] = useState('greeting');
    const [sanctionData, setSanctionData] = useState(null);

    useEffect(() => {
        // Start a new chat session on mount
        startNewSession();
    }, []);

    const startNewSession = async () => {
        try {
            const response = await fetch('/api/chat/start', {
                method: 'POST',
            });
            const data = await response.json();
            setSessionId(data.session_id);
            setInitialMessage(data.message);
            setCurrentStage(data.stage);
            setIsLoading(false);
        } catch (error) {
            console.error('Failed to start session:', error);
            setIsLoading(false);
        }
    };

    const handleSessionUpdate = (sessionData) => {
        if (sessionData.customer) setCustomer(sessionData.customer);
        if (sessionData.application) setApplication(sessionData.application);
        if (sessionData.stage) setCurrentStage(sessionData.stage);
        if (sessionData.metadata) setSanctionData({ ...sessionData.metadata, session_id: sessionId });
    };

    return (
        <div className="app">
            <header className="app-header">
                <div className="header-content">
                    <div className="logo-section">
                        <h1 className="logo-text">
                            <span className="gradient-text">Tata Capital</span>
                        </h1>
                        <p className="tagline">Personal Loan Assistant</p>
                    </div>
                    <div className="header-badge">
                        <span className="badge-dot pulse"></span>
                        <span>AI Powered</span>
                    </div>
                </div>
            </header>

            <main className="app-main">
                {isLoading ? (
                    <div className="loading-container">
                        <div className="loading-spinner"></div>
                        <p>Initializing your personal loan assistant...</p>
                    </div>
                ) : (
                    <div className="three-column-layout">
                        <div className="left-panel">
                            <ChatInterface
                                sessionId={sessionId}
                                initialMessage={initialMessage}
                                onSessionUpdate={handleSessionUpdate}
                            />
                        </div>
                        <div className="center-panel">
                            <LoanSummaryCard
                                application={application}
                                customer={customer}
                            />
                        </div>
                        <div className="right-panel">
                            <AgentStatusPanel
                                currentStage={currentStage}
                                application={application}
                                sanctionData={sanctionData}
                            />
                        </div>
                    </div>
                )}
            </main>

            <footer className="app-footer">
                <p>© 2024 Tata Capital Financial Services Limited. All rights reserved.</p>
                <p className="footer-disclaimer">
                    This is a demo AI assistant. For actual loan applications, please visit{' '}
                    <a href="https://www.tatacapital.com" target="_blank" rel="noopener noreferrer">
                        www.tatacapital.com
                    </a>
                </p>
            </footer>
        </div>
    );
}

export default App;
