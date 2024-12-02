import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const CompanyDetails = () => {
  const { companyId } = useParams();
  const [darkMode, setDarkMode] = useState(false);
  const [companyDetails, setCompanyDetails] = useState(null); // State to hold company details
  const [loading, setLoading] = useState(true); // State for loading
  const [error, setError] = useState(null); // State for error handling

  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.classList.add('dark');
    }

    // Fetch company details based on companyId from localhost:5000 API
    fetch(`http://localhost:8080/api/companies/${companyId}`) // API for company details
      .then(response => response.json())
      .then(data => {
        setCompanyDetails(data);
        // Fetch stock price for the company
        fetch(`http://localhost:8080/api/companies/${companyId}`)  // API for stock price
          .then(response => response.json())
          .then(stockData => {
            setCompanyDetails(prevDetails => ({ ...prevDetails, price: stockData.price }));
          })
          .catch(err => {
            setError('Failed to load stock price');
          });
        setLoading(false); // Data has been loaded
      })
      .catch(err => {
        setError('Failed to load company details');
        setLoading(false);
      });
  }, [companyId]);

  const toggleDarkMode = () => {
    setDarkMode(prevMode => {
      const newMode = !prevMode;
      localStorage.setItem('darkMode', newMode.toString());
      if (newMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return newMode;
    });
  };

  if (loading) {
    return <div>Loading...</div>; // Show loading state
  }

  if (error) {
    return <div>{error}</div>; // Show error message if there's an error
  }

  return (
    <div className={`min-h-screen py-8 ${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-4xl font-semibold text-center">Company Details</h1>
          <button
            onClick={toggleDarkMode}
            className="bg-gray-800 text-white p-2 rounded-md focus:outline-none hover:bg-gray-700"
          >
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>
        <div className={`p-6 rounded-lg shadow-md ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} transition-all duration-300`}>
          {companyDetails ? (
            <>
              <p className="text-xl mb-4">Details for company: {companyDetails.name}</p>
              <p className="text-lg">{companyDetails.short_name}</p>
              <p className="text-lg">Price: ${companyDetails.price}</p> {/* Display the price */}
              {/* Add more company details as needed */}
            </>
          ) : (
            <p>No details available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanyDetails;
