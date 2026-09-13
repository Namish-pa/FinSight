import React, { useEffect, useState } from 'react';
import KPIs from './components/KPIs';
import Forecast from './components/Forecast';
import QueryEngine from './components/QueryEngine';
import { fetchKPIs, fetchForecast } from './api';

function App() {
    const [kpiData, setKpiData] = useState(null);
    const [forecastData, setForecastData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [kpis, forecast] = await Promise.all([
                    fetchKPIs(),
                    fetchForecast()
                ]);
                setKpiData(kpis);
                setForecastData(forecast);
            } catch (err) {
                setError(err.message);
            }
        };
        loadData();
    }, []);

    return (
        <div className="app-container">
            <h1>FinSight</h1>
            
            {error && (
                <div className="error-text" style={{ marginBottom: '2rem' }}>
                    Error loading data: {error}. Is the backend running on port 8000?
                </div>
            )}

            <QueryEngine />
            <KPIs data={kpiData} />
            <Forecast data={forecastData} />
            
            <footer style={{ marginTop: '4rem', textAlign: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '1rem', color: 'var(--muted-text)', fontSize: '0.9em' }}>
                FinSight &copy; 2026. Data is strictly deterministic and verifiable.
            </footer>
        </div>
    );
}

export default App;
