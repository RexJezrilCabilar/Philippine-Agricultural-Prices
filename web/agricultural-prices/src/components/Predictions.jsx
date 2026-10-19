import React, { useState, useEffect, useMemo } from 'react';
import Papa from 'papaparse';


export default function Predictions({forecastData, selectedCommodity, selectedGeolocation}) {
    const [rawData, setRawData] = useState([]);
    const [filteredData, setFilteredData] = useState([]);

    useEffect(() => {
        Papa.parse(forecastData, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                setRawData(results.data);
            }
        })       
    }), [forecastData];

    useEffect(() => {
        const filtered = rawData.filter(row => 
            selectedCommodity.includes(row["Commodity"]) && 
            selectedGeolocation.includes(row["Geolocation"])
        );
        setFilteredData(filtered);
    }, [rawData, selectedCommodity, selectedGeolocation]);

    const predictions = useMemo(() => {
        const grouped = Object.groupBy(filteredData, row => `${row["Commodity"]}-${row["Geolocation"]}`);
        return grouped;
    }, [filteredData]);

    {/* Getting the current month number */}
    const getCurrentMonth = () => {
        return new Date().getMonth() + 1;
    };

    return (
        <div>
            <h2><strong>Predictions</strong></h2>
            {Object.entries(predictions).map(([key, rows]) => (
                <div key={key} className="m-2">
                    <h3>{key}</h3>
                    <p><strong>Geolocation:</strong> {rows[0]["Geolocation"]}</p>
                    <p><strong>Predicted Price this Month:</strong> {rows?.[0]?.[`Forecast_${getCurrentMonth()}`] ? Number(rows[0][`Forecast_${getCurrentMonth()}`]).toFixed(2) : 'N/A'}</p>
                    <p><strong>Predicted Price next Month:</strong> {rows?.[0]?.[`Forecast_${getCurrentMonth() + 1}`] ? Number(rows[0][`Forecast_${getCurrentMonth() + 1}`]).toFixed(2) : 'N/A'}</p>
                    <p><strong>Predicted Price in 2 Months:</strong> {rows?.[0]?.[`Forecast_${getCurrentMonth() + 2}`] ? Number(rows[0][`Forecast_${getCurrentMonth() + 2}`]).toFixed(2) : 'N/A'}</p>
                    
                </div>
            ))}    
        </div>
    )
}