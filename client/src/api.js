const BASE_URL = 'http://localhost:8000/api';

export const fetchKPIs = async () => {
    const response = await fetch(`${BASE_URL}/kpis`);
    if (!response.ok) throw new Error('Failed to fetch KPIs');
    return response.json();
};

export const fetchForecast = async () => {
    const response = await fetch(`${BASE_URL}/forecast`);
    if (!response.ok) throw new Error('Failed to fetch Forecast');
    return response.json();
};

export const askQuery = async (question) => {
    const response = await fetch(`${BASE_URL}/ask`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
    });
    if (!response.ok) throw new Error('Failed to execute query');
    return response.json();
};
