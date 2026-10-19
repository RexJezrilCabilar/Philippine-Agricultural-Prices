import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';

export default function Forecast({forecastData}) {

    const [commodityOptions, setCommodityOptions] = useState([]);
    const [geolocationOptions, setGeolocationOptions] = useState([]);  
    const [selectedCommodity, setSelectedCommodity] = useState('');
    const [selectedGeolocation, setSelectedGeolocation] = useState('');

    useEffect(() => {
        Papa.parse(forecastData, {
        header: true,
        complete: (results) => {
            const commodities = new Set();
            const geolocations = new Set();
            
            results.data.forEach(row => {
                if (row["Commodity"]) commodities.add(row["Commodity"]);
                if (row["Geolocation"]) geolocations.add(row["Geolocation"]);
            });
            
            setCommodityOptions(Array.from(commodities));
            setGeolocationOptions(Array.from(geolocations));
        }
    })
    }, [forecastData]);


    return (
        <div>
             <label htmlFor="commodity-select">Commodity:</label>
                <select id="commodity-select" value={selectedCommodity} onChange={(e) => setSelectedCommodity(e.target.value)}>
                    <option value="">Select a commodity</option>
                        {commodityOptions.map((commodity, index) => (
                            <option key={index} value={commodity}>{commodity}</option>
                        ))}
                </select>
             <label htmlFor="geolocation-select">Geolocation:</label>
                <select id="geolocation-select" value={selectedGeolocation} onChange={(e) => setSelectedGeolocation(e.target.value)}>
                    <option value="">Select a geolocation</option>
                        {geolocationOptions.map((geolocation, index) => (
                            <option key={index} value={geolocation}>{geolocation}</option>
                        ))}
                </select>
        </div>



    )

}

