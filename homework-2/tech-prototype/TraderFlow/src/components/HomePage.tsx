import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  const [darkMode, setDarkMode] = useState(false); // State to track dark mode
  const [companies, setCompanies] = useState([]);  // State to store fetched companies
  const [loading, setLoading] = useState(true);     // State to track loading state
  const [error, setError] = useState(null);         // State to track errors

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.documentElement.classList.add('dark'); // Apply dark class
    } else {
      document.documentElement.classList.remove('dark'); // Remove dark class
    }
  };

  // Fetch companies from the Flask API using async/await
  const fetchCompanies = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/companies');  // API endpoint to fetch companies
      if (!response.ok) {  // Check if the response is successful
        throw new Error('Failed to fetch companies');
      }
      const data = await response.json();  // Parse the response as JSON

      // Fetch the stock prices for each company
      const companiesWithPrices = await Promise.all(data.map(async (company) => {
        const stockResponse = await fetch(`http://localhost:8080/api/companies/${company.id}`);
        const stockData = await stockResponse.json();
        return { ...company, price: stockData.price };  // Add the price to the company data
      }));

      setCompanies(companiesWithPrices);     // Set companies state with the fetched data
    } catch (error) {
      setError(error);        // Set error state if there's an issue
    } finally {
      setLoading(false);      // Set loading to false once data is fetched or error occurred
    }
  };

  // Fetch companies when the component mounts
  useEffect(() => {
    fetchCompanies();  // Call the async fetch function
  }, []); // Empty dependency array ensures this runs once when the component mounts

  return (
    <div className={`min-h-screen py-8 ${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
      <div className="container mx-auto px-4">
        {/* Header section with title and slogan */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold">TraderFlow</h1>
          <p className="text-xl text-gray-500 mt-2">Elevating your trading experience.</p>
        </div>

        <div className="flex justify-between items-center mb-6">
          <h2 className="text-4xl font-semibold text-center">Company List</h2>
          <button
            onClick={toggleDarkMode}
            className="bg-gray-800 text-white p-2 rounded-md focus:outline-none hover:bg-gray-700"
          >
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>

        {/* Display loading spinner or error message */}
        {loading && <p>Loading companies...</p>}
        {error && <p className="text-red-500">Error fetching companies: {error.message}</p>}

        {/* Display companies if data is available */}
        {!loading && !error && (
          <ul className="space-y-4">
            {companies.map(company => (
              <li
                key={company.id}
                className={`p-4 rounded-lg shadow-md ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} hover:${darkMode ? 'bg-gray-700' : 'bg-gray-200'} transition-all duration-300`}
              >
                <Link
                  to={`/company/${company.id}`}
                  className={`text-xl font-medium ${darkMode ? 'text-blue-400 hover:text-blue-600' : 'text-blue-600 hover:text-blue-800'}`}
                >
                  <div className="flex justify-between">
                    <span>{company.name}</span>
                    <span className="text-sm text-gray-400">{company.short_name}</span>
                  </div>
                  <div className="text-lg mt-2">Stock Price: ${company.price}</div> {/* Display stock price */}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default HomePage;
