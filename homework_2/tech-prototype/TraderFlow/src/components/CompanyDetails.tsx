import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Company } from '../utilities/types';
import ApiError from '../utilities/apierror';
import Indicators from './Indicators';

const CompanyDetails = () => {
    const { companyId } = useParams();
    const [darkMode, setDarkMode] = useState(false);
    const [companyDetails, setCompanyDetails] = useState<Company | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<ApiError | null>(null);
    const [priceHistory, setPriceHistory] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState<'history' | 'indicators'>('history');

    const fetchCompanyDetails = useCallback(async () => {
        try {
            setLoading(true);
            const response = await fetch(`http://localhost:5000/api/companies/${companyId}`);
            if (!response.ok) throw new Error('Failed to fetch company details');
            const data = await response.json();
            setCompanyDetails(data);
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
            const response = await fetch(`http://localhost:5000/api/companies/${companyId}/stock-data`);
            if (!response.ok) throw new Error('Failed to fetch stock data');
            const data = await response.json();
            setPriceHistory(data.content);
        } catch (err) {
            if (err instanceof Error) {
                setError(new ApiError(500, err.message, 'Failed to fetch stock data'));
            }
        } finally {
            setLoading(false);
        }
    }, [companyId]);

    useEffect(() => {
        fetchCompanyDetails();
        fetchStockData();
    }, [companyId, fetchCompanyDetails, fetchStockData]);

    const toggleDarkMode = () => {
        setDarkMode(prevMode => {
            const newMode = !prevMode;
            localStorage.setItem('darkMode', newMode.toString());
            document.documentElement.classList.toggle('dark', newMode);
            return newMode;
        });
    };

    const renderPriceHistory = () => (
        <>
            <h2 className="text-2xl mt-4 font-semibold">Stock History</h2>
            <table className={`min-w-full table-auto border border-gray-300 rounded-lg overflow-hidden ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} overflow-hidden`}>
                <thead>
                    <tr className={`${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
                        <th className="border px-4 py-2">Date</th>
                        <th className="border px-4 py-2">Close</th>
                        <th className="border px-4 py-2">Min</th>
                        <th className="border px-4 py-2">Max</th>
                        <th className="border px-4 py-2">Volume</th>
                        <th className="border px-4 py-2">Signal</th>
                    </tr>
                </thead>
                <tbody>
                    {priceHistory.map((item, index) => (
                        <tr key={index} className="text-center">
                            <td className="border px-4 py-2">{item.date}</td>
                            <td className="border px-4 py-2">{item.price} mkd</td>
                            <td className="border px-4 py-2">{item.min} mkd</td>
                            <td className="border px-4 py-2">{item.max} mkd</td>
                            <td className="border px-4 py-2">{item.volume}</td>
                            <td className={`border px-4 py-2 ${item.signal === 'buy' ? 'text-green-500' : item.signal === 'sell' ? 'text-red-500' : 'text-yellow-500'}`}>
                                {item.signal}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </>
    );

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
                            {activeTab === 'history' ? renderPriceHistory() : <Indicators companyId={companyId} darkMode={darkMode} />}
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
