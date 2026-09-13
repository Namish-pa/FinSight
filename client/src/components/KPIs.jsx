import React from 'react';

export default function KPIs({ data }) {
    if (!data) return <div>Loading KPIs...</div>;

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
    };

    const agingRows = [
        { label: 'Not Yet Due', key: 'not_yet_due' },
        { label: '0-30 Days', key: '0-30' },
        { label: '31-60 Days', key: '31-60' },
        { label: '61-90 Days', key: '61-90' },
        { label: '90+ Days', key: '90+' },
    ];

    return (
        <div className="section">
            <h2>Key Performance Indicators</h2>
            <div className="kpi-grid">
                <div className="card">
                    <div className="data-label">Days Sales Outstanding</div>
                    <div className="data-number">{data.dso} Days</div>
                </div>
                <div className="card">
                    <div className="data-label">Cash Runway</div>
                    <div className="data-number">{data.cash_runway} Months</div>
                </div>
            </div>

            <h3>Accounts Receivable Aging</h3>
            <table>
                <thead>
                    <tr>
                        <th>Bucket</th>
                        <th>Invoices</th>
                        <th>Total Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {agingRows.map(row => {
                        const bucket = data.aging_buckets[row.key];
                        if (!bucket) return null;
                        return (
                            <tr key={row.key}>
                                <td>{row.label}</td>
                                <td className="data-number">{bucket.count}</td>
                                <td className="data-number">{formatCurrency(bucket.total_amount)}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}
