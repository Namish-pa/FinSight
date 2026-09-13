import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

export default function Forecast({ data }) {
    if (!data) return <div>Loading Forecast...</div>;

    // We will combine historical and forecast data, taking the last 6 months of historical
    // plus the 3 months of forecast to create a continuous line.
    
    const recentHistory = data.historical.slice(-6).map(item => ({
        month: item.month,
        net: item.net,
        type: 'historical'
    }));

    const forecast = data.forecast.map(item => ({
        month: item.month,
        net: item.forecast_net,
        type: 'forecast'
    }));

    const chartData = [...recentHistory, ...forecast];

    // Minimalist custom tooltip
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const value = payload[0].value;
            const type = payload[0].payload.type;
            const formatted = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
            return (
                <div style={{ background: '#fff', border: '1px solid #1a1a1a', padding: '10px', fontFamily: 'var(--font-mono)' }}>
                    <p style={{ margin: 0, fontWeight: 'bold', fontFamily: 'var(--font-serif)' }}>{label} {type === 'forecast' ? '(Proj)' : ''}</p>
                    <p style={{ margin: 0 }}>{formatted}</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="section card">
            <h2>Cash Flow Forecast</h2>
            <div className="data-label" style={{ marginBottom: '1.5rem' }}>
                Model: Linear Regression (3-Month Projection)
                {data.excluded_month && 
                    <span> | Note: {data.excluded_month.month} excluded from fit due to partial data.</span>
                }
            </div>
            
            <div style={{ width: '100%', height: 300 }}>
                <ResponsiveContainer>
                    <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ccc" vertical={false} />
                        <XAxis 
                            dataKey="month" 
                            stroke="#1a1a1a" 
                            tick={{ fontFamily: 'var(--font-mono)', fontSize: 12 }} 
                            tickLine={false} 
                            axisLine={false}
                        />
                        <YAxis 
                            stroke="#1a1a1a" 
                            tickFormatter={(val) => `$${(val / 1000000).toFixed(1)}M`}
                            tick={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}
                            tickLine={false}
                            axisLine={false}
                            width={80}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <ReferenceLine y={0} stroke="#1a1a1a" strokeDasharray="3 3" />
                        <Line 
                            type="monotone" 
                            dataKey="net" 
                            stroke="#1a1a1a" 
                            strokeWidth={2}
                            dot={{ fill: '#1a1a1a', stroke: 'none', r: 4 }}
                            activeDot={{ r: 6 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
