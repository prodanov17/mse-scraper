import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Company, PricePrediction, Sentiment } from '../utilities/types';
import ApiError from '../utilities/apierror';
import api from '../utilities/fetching';
import StockData from './StockData';

const CompanyDetails = () => {
    const { companyId } = useParams(); // Get companyKey from URL params
    const [darkMode, setDarkMode] = useState(false);
    const [companyDetails, setCompanyDetails] = useState<Company | null>(null); // State to hold company details
    const [loading, setLoading] = useState(true); // State for loading
    const [error, setError] = useState<ApiError | null>(null); // State for error handling
    const [sentiment, setSentiment] = useState<Sentiment | null>(null);
    const [predictedPrice, setPredictedPrice] = useState<PricePrediction | null>(null);
    const [priceError, setPriceError] = useState<ApiError | null>(null);
    const [sentimentError, setSentimentError] = useState<ApiError | null>(null);

    const fetchCompanyDetails = useCallback(async () => {
        try {
            setLoading(true); // Start loading

            // Fetch company data from the Flask API
            const response = await api.get(`companies/${companyId}/price-history`) as Company;

            setCompanyDetails(response);
        } catch (err) {
            if (err instanceof Error) {
                setError(new ApiError(500, err.message, 'Failed to fetch company details'));
            }
        } finally {
            setLoading(false); // Stop loading
        }
    }, [companyId]);

    const fetchPrice = useCallback(async () => {
        try {
            setLoading(true); // Start loading
            console.log(`Fetching data for company: ${companyId}`);

            // Fetch company data from the Flask API
            const response = await fetch(`http://localhost:8082/api/companies/${companyId}/predict`);
            console.log(`Response status: ${response.status}`);

            if (!response.ok) {
                throw new Error('Failed to fetch company details');
            }

            const data = await response.json();
            setPredictedPrice(data);
            console.log(data);
        } catch (err) {
            if (err instanceof Error) {
                setPriceError(new ApiError(500, err.message, 'Failed to fetch company details'));
            }
            console.error('Error fetching company details:', err);
        } finally {
            setLoading(false); // Stop loading
        }

    }, [companyId]);

    const fetchSentiment = useCallback(async () => {
        try {
            setLoading(true); // Start loading
            console.log(`Fetching data for company: ${companyId}`);

            // Fetch company data from the Flask API
            const response = await fetch(`http://localhost:8082/api/companies/${companyId}/news/sentiment`);
            console.log(`Response status: ${response.status}`);

            if (!response.ok) {
                throw new Error('Failed to fetch company details');
            }

            const data = await response.json();
            setSentiment(data);
            console.log(data);
        } catch (err) {
            if (err instanceof Error) {
                setSentimentError(new ApiError(500, err.message, 'Failed to fetch company details'));
            }
            console.error('Error fetching company details:', err);
        } finally {
            setLoading(false); // Stop loading
        }

    }, [companyId]);

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
    }, [companyId, fetchCompanyDetails, fetchSentiment, fetchPrice]);


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
    const sentimentColor = (sentiment: string) => {
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
        return <div>{error.message}</div>; // Show error message if there's an error
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
                            <p className="text-xl mb-4">Details for company: {companyDetails.short_name}</p>
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


                            {/* Display tab groups */}
                            {/* If tab is price history - display StockData */}
                            {/* If tab is indicators - display Indicators */}
                            {companyDetails && <StockData stockData={companyDetails.stock_data || null} />}
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
