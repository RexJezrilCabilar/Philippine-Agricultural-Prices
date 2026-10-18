import React, { useState, useEffect } from 'react'
import Home from './components/Home'


export default function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/data/agricultural-prices.json')
      .then(response => response.json())
      .then(jsonData => setData(jsonData))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    <div className="App bg-green-400">
      <header className="App-header bg-green-600 ">
        <h1>Agricultural Prices</h1>
      </header>
      <main>
        {data ? <Home data={data} /> : <p>Loading data...</p>}
      </main>
    </div>
  );
}