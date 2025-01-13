import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Company, Page, PricePrediction, Sentiment, StockData } from '../utilities/types';
import ApiError from '../utilities/apierror';
import Indicators from './Indicators';
import api from '../utilities/fetching';
import StockDataTable from './StockData';

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


const CompanyDetails = () => {
    const { companyId } = useParams();
    const [darkMode, setDarkMode] = useState(false);
    const [companyDetails, setCompanyDetails] = useState<Company | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<ApiError | null>(null);
    const [priceHistory, setPriceHistory] = useState<Page<StockData> | null>(null);
    const [sentiment, setSentiment] = useState<Sentiment | null>(null);
    const [predictedPrice, setPredictedPrice] = useState<PricePrediction | null>(null);

    const [activeTab, setActiveTab] = useState<'history' | 'indicators'>('history');

    const fetchCompanyDetails = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.get(`companies/${companyId}`) as Company;
            setCompanyDetails(response);
        } catch (err) {
            if (err instanceof Error) {
                setError(new ApiError(500, err.message, 'Failed to fetch company details'));
            }
        } finally {
            setLoading(false);
        }
    }, [companyId]);

    const fetchStockData = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.get(`companies/${companyId}/price-history`) as { stock_data: Page<StockData> };
            setPriceHistory(response.stock_data);
        } catch (err) {
            if (err instanceof Error) {
                setError(new ApiError(500, err.message, 'Failed to fetch stock data'));
            }
        } finally {
            setLoading(false);
        }
    }, [companyId]);

    const fetchPrice = useCallback(async () => {
        try {
            setLoading(true); // Start loading

            // Fetch company data from the Flask API
            const response = await api.get(`companies/${companyId}/predict`) as PricePrediction;

            setPredictedPrice(response);
        } catch (err) {
            console.error('Error fetching company details:', err);
        } finally {
            setLoading(false); // Stop loading
        }

    }, [companyId]);

    const fetchSentiment = useCallback(async () => {
        try {
            setLoading(true); // Start loading

            // Fetch company data from the Flask API
            const response = await api.get(`companies/${companyId}/news/sentiment`) as Sentiment;

            setSentiment(response);
        } catch (err) {
            console.error('Error fetching company details:', err);
        } finally {
            setLoading(false); // Stop loading
        }

    }, [companyId]);


    useEffect(() => {
        fetchCompanyDetails();
        fetchStockData();
        fetchPrice();
        fetchSentiment();
    }, [companyId, fetchCompanyDetails, fetchStockData, fetchPrice, fetchSentiment]);

    const toggleDarkMode = () => {
        setDarkMode(prevMode => {
            const newMode = !prevMode;
            localStorage.setItem('darkMode', newMode.toString());
            document.documentElement.classList.toggle('dark', newMode);
            return newMode;
        });
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="text-red-500">{error.message}</div>;

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
                            <p className="text-xl mb-4">Details for company: {companyDetails.short_name}</p>
                            <p className="">Price: {companyDetails.price} mkd.</p>
                            <p className="mb-4">Price change: {companyDetails.price_change.toFixed(2)}%</p>
                            <p className="text-lg">
                                Sentiment: {' '}
                                {!sentiment
                                    ? "N/A"
                                    : sentiment
                                        ? <span className={sentimentColor(sentiment.sentiment)}>{sentiment.sentiment}</span>
                                        : "Loading..."}
                            </p>

                            <p className="text-lg">
                                Predicted Price:{' '}
                                {!predictedPrice
                                    ? "N/A"
                                    : predictedPrice
                                        ? `${predictedPrice.prediction.toFixed(2)} mkd.`
                                        : "Loading..."}
                            </p>



                            {/* Tab Buttons */}
                            <div className="flex mb-4">
                                <button
                                    className={`flex-1 p-2 rounded-md ${activeTab === 'history' ? 'bg-blue-500 text-white' : darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-800'}`}
                                    onClick={() => setActiveTab('history')}
                                >
                                    Stock History
                                </button>
                                <button
                                    className={`flex-1 p-2 rounded-md ${activeTab === 'indicators' ? 'bg-blue-500 text-white' : darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-800'}`}
                                    onClick={() => setActiveTab('indicators')}
                                >
                                    Indicators
                                </button>
                            </div>

                            {/* Render content based on active tab */}
                            {activeTab === 'history' ? <StockDataTable stockData={priceHistory} /> : <Indicators companyId={companyId || ""} darkMode={darkMode} />}
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
