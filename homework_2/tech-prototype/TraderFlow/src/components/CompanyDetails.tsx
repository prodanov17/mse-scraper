import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const CompanyDetails = () => {
    const { companyId } = useParams(); // Get companyKey from URL params
    const [darkMode, setDarkMode] = useState(false);
    const [companyDetails, setCompanyDetails] = useState(null); // State to hold company details
    const [loading, setLoading] = useState(true); // State for loading
    const [error, setError] = useState(null); // State for error handling
    const [sentiment, setSentiment] = useState(null);
    const [predictedPrice, setPredictedPrice] = useState(null);
    const [priceError, setPriceError] = useState(null);
    const [sentimentError, setSentimentError] = useState(null);

    const fetchCompanyDetails = async () => {
        try {
            setLoading(true); // Start loading
            console.log(`Fetching data for company: ${companyId}`);

            // Fetch company data from the Flask API
            const response = await fetch(`http://localhost:8080/api/companies/${companyId}/price-history`);
            console.log(`Response status: ${response.status}`);

            if (!response.ok) {
                throw new Error('Failed to fetch company details');
            }

            const data = await response.json();
            setCompanyDetails(data);
            console.log(data);
        } catch (err) {
            setError(err.message || 'Failed to load company details');
            console.error('Error fetching company details:', err);
        } finally {
            setLoading(false); // Stop loading
        }
    };

    const fetchPrice = async () => {
        try {
            setLoading(true); // Start loading
            console.log(`Fetching data for company: ${companyId}`);

            // Fetch company data from the Flask API
            const response = await fetch(`http://localhost:8080/api/companies/${companyId}/predict`);
            console.log(`Response status: ${response.status}`);

            if (!response.ok) {
                throw new Error('Failed to fetch company details');
            }

            const data = await response.json();
            setPredictedPrice(data);
            console.log(data);
        } catch (err) {
            setPriceError(err.message || 'No price found');
            console.error('Error fetching company details:', err);
        } finally {
            setLoading(false); // Stop loading
        }

    }

    const fetchSentiment = async () => {
        try {
            setLoading(true); // Start loading
            console.log(`Fetching data for company: ${companyId}`);

            // Fetch company data from the Flask API
            const response = await fetch(`http://localhost:8080/api/companies/${companyId}/news/sentiment`);
            console.log(`Response status: ${response.status}`);

            if (!response.ok) {
                throw new Error('Failed to fetch company details');
            }

            const data = await response.json();
            setSentiment(data);
            console.log(data);
        } catch (err) {
            setSentimentError(err.message || 'No sentiment found');
            console.error('Error fetching company details:', err);
        } finally {
            setLoading(false); // Stop loading
        }

    }

    // Fetch company details when component mounts or companyKey changes
    useEffect(() => {
        // Get dark mode preference from localStorage
        const savedDarkMode = localStorage.getItem('darkMode') === 'true';
        setDarkMode(savedDarkMode);
        if (savedDarkMode) {
            document.documentElement.classList.add('dark');
        }


        fetchCompanyDetails();
        fetchSentiment();
        fetchPrice();
    }, [companyId]); // Rerun the effect when companyKey changes


    // Toggle dark mode and save the preference to localStorage
    const toggleDarkMode = () => {
        setDarkMode((prevMode) => {
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

    // Display a default sentiment color (if no sentiment is provided)
    const sentimentColor = (sentiment) => {
        switch (sentiment) {
            case 'positive':
                return 'text-green-500'; // Green for positive
            case 'negative':
                return 'text-red-500'; // Red for negative
            case 'neutral':
                return 'text-blue-500'; // Blue for neutral
            default:
                return 'text-gray-500'; // Default gray if no sentiment
        }
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

                {/* Company details */}
                <div className={`p-6 rounded-lg shadow-md ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} transition-all duration-300`}>
                    {companyDetails ? (
                        <>
                            <p className="text-xl mb-4">Details for company: {companyDetails.company_key}</p>
                            <p className="text-lg">Price: {companyDetails.price} mkd.</p>
                            <p className="text-lg">
                                Sentiment: {' '}
                                {sentimentError
                                    ? "N/A"
                                    : sentiment
                                        ? <span className={sentimentColor(sentiment.sentiment)}>{sentiment.sentiment}</span>
                                        : "Loading..."}
                            </p>

                            <p className="text-lg">
                                Predicted Price:{' '}
                                {priceError
                                    ? "N/A"
                                    : predictedPrice
                                        ? `${predictedPrice.prediction.toFixed(2)} mkd.`
                                        : "Loading..."}
                            </p>


                            {/* Stock History */}
                            <h2 className="text-2xl mt-6 mb-4">Stock History</h2>
                            {companyDetails.stock_data && companyDetails.stock_data.content && companyDetails.stock_data.content.length > 0 ? (
                                <table className="table-auto w-full text-sm text-left">
                                    <thead className="border-b">
                                        <tr>
                                            <th className="px-4 py-2">Date</th>
                                            <th className="px-4 py-2">Last Trade Price</th>
                                            <th className="px-4 py-2">Max</th>
                                            <th className="px-4 py-2">Min</th>
                                            <th className="px-4 py-2">Avg.</th>
                                            <th className="px-4 py-2">Price % Chg.</th>
                                            <th className="px-4 py-2">Volume</th>
                                            <th className="px-4 py-2">Turnover in BEST (Denars)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {companyDetails.stock_data.content.map((entry, index) => (
                                            <tr key={index} className="border-b">
                                                <td className="px-4 py-2">{entry.date}</td>
                                                <td className="px-4 py-2">{entry.price.toFixed(2)}</td>
                                                <td className="px-4 py-2">{entry.max.toFixed(2)}</td>
                                                <td className="px-4 py-2">{entry.min.toFixed(2)}</td>
                                                <td className="px-4 py-2">{entry.average_price.toFixed(2)}</td>
                                                <td className="px-4 py-2">{entry.price_change.toFixed(2)}%</td>
                                                <td className="px-4 py-2">{entry.volume}</td>
                                                <td className="px-4 py-2">{entry.best_turnover.toLocaleString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <p>No stock history available</p>
                            )}
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
