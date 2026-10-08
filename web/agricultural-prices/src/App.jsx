import React, { useState, useEffect } from 'react'
import './App.css'

export default function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/data/agricultural-prices.json')
      .then(response => response.json())
      .then(jsonData => setData(jsonData))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Agricultural Prices</h1>
      </header>
      <main>
        {data ? (
          <div>
            <h2>Price Data</h2>
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        ) : (
          <p>Loading data...</p>
        )}
      </main>
    </div>
  );
}