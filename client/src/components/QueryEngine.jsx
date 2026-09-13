import React, { useState } from 'react';
import { askQuery } from '../api';

export default function QueryEngine() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError(null);
        try {
            const data = await askQuery(query);
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="section">
            <h2>Query Engine</h2>
            
            <form onSubmit={handleSubmit} className="query-input-container">
                <input 
                    type="text" 
                    className="query-input"
                    placeholder="Ask a question about the financial data..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={loading}
                />
                <button type="submit" className="query-button" disabled={loading || !query.trim()}>
                    {loading ? 'Asking...' : 'Ask'}
                </button>
            </form>

            {error && (
                <div className="error-text">
                    Error: {error}
                </div>
            )}

            {result && (
                <div className="query-results">
                    <div className="answer-box">
                        <strong>Answer:</strong> {result.summary}
                    </div>

                    {result.rows && result.rows.length > 0 && (
                        <table>
                            <thead>
                                <tr>
                                    {Object.keys(result.rows[0]).map(col => (
                                        <th key={col}>{col}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {result.rows.map((row, i) => (
                                    <tr key={i}>
                                        {Object.values(row).map((val, j) => (
                                            <td key={j} className="data-number">{String(val)}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                    
                    <div className="data-label" style={{ marginTop: '1rem' }}>
                        SQL Executed: <span className="data-number" style={{ fontSize: '1em' }}>{result.sql}</span>
                    </div>
                </div>
            )}
        </div>
    );
}
