import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import Predictions from './Predictions';

export default function Forecast({forecastData}) {

    const [commodityOptions, setCommodityOptions] = useState([]);
    const [geolocationOptions, setGeolocationOptions] = useState([]);  
    const [selectedCommodity, setSelectedCommodity] = useState([]);
    const [selectedGeolocation, setSelectedGeolocation] = useState([]);

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

    {/* Handlers for checkbox changes */}
    const handleCommodityChange = (e) => {
        const {checked, value} = e.target;

        setSelectedCommodity((prevSelected) => 
            checked ? [...prevSelected, value] : prevSelected.filter(item => item !== value)
        )
    };

    const handleGeolocationChange = (e) => {
        const {checked, value} = e.target;

        setSelectedGeolocation((prevSelected) => 
            checked ? [...prevSelected, value] : prevSelected.filter(item => item !== value)
        )
    };

    {/* Handlers for the imported Predictions component */}
    
    const[isVisible, setIsVisible] = useState(false);

    const handleClick = () => {
        setIsVisible(true);
    };

    return (
        <div className="flex flex-col gap-6 w-full m-10 max-w-4xl p-6 bg-green-300 border border-green-00 shadow-sm rounded-xl">
            

            <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Select Commodities</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                    {commodityOptions.map((commodity) => {
                        const isChecked = selectedCommodity.includes(commodity);
                        return (
                            <label 
                                key={commodity} 
                                className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer select-none transition-all duration-150
                                    ${isChecked 
                                        ? 'border-blue-500 bg-blue-50/50 text-blue-700 font-medium' 
                                        : 'border-gray-200 bg-gray-50 hover:bg-gray-100 text-gray-700'
                                    }`}
                            >
                                <input
                                    type="checkbox"
                                    value={commodity}
                                    checked={isChecked}
                                    onChange={handleCommodityChange}
                                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                />
                                <span className="text-sm truncate">{commodity}</span>
                            </label>
                        );
                    })}
                </div>
            </div>

            {/* Visual Divider */}
            <hr className="border-gray-200" />

            {/* Section 2: Geolocations */}
            <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Select Geolocations</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                    {geolocationOptions.map((geolocation) => {
                        const isChecked = selectedGeolocation.includes(geolocation);
                        return (
                            <label 
                                key={geolocation} 
                                className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer select-none transition-all duration-150
                                    ${isChecked 
                                        ? 'border-blue-500 bg-blue-50/50 text-blue-700 font-medium' 
                                        : 'border-gray-200 bg-gray-50 hover:bg-gray-100 text-gray-700'
                                    }`}
                            >
                                <input
                                    type="checkbox"
                                    value={geolocation}
                                    checked={isChecked}
                                    onChange={handleGeolocationChange}
                                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                />
                                <span className="text-sm truncate">{geolocation}</span>
                            </label>
                        );
                    })}
                </div>
            </div>

            <div className="mt-6">
                <button
                    onClick={handleClick}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    Show Predictions
                </button>
                {isVisible && forecastData && selectedCommodity.length > 0 && selectedGeolocation.length > 0 && <Predictions forecastData={forecastData} selectedCommodity={selectedCommodity} selectedGeolocation={selectedGeolocation} />}
            </div>

        </div>
    );

}

