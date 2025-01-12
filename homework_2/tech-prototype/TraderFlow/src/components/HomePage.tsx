import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Company } from '../utilities/types';
import ApiError from '../utilities/apierror';

const HomePage: React.FC = () => {
    const [darkMode, setDarkMode] = useState(false);
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<ApiError | null>(null);

    // Toggle dark mode
    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
        if (!darkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    };

    const fetchCompanies = async () => {
        setLoading(true)
        try {
            const response = await fetch('http://localhost:8082/api/companies');
            if (!response.ok) {
                throw new Error('Failed to fetch companies');
            }
            const data = await response.json() as Company[];

            const companies = data.filter(company => company.price !== null);
            setCompanies(companies);
        } catch (error) {
            if (error instanceof Error) {
                setError(new ApiError(500, error.message, 'Failed to fetch companies'));
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCompanies();
    }, []);

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

                {loading && <p>Loading companies...</p>}
                {error && <p className="text-red-500">Error fetching companies: {error.message}</p>}

                {/* Display companies if data is available */}
                {!loading && !error && (
                    <ul className="space-y-4">
                        {companies.map(company => (
                            <li
                                key={company.short_name}
                                className={`p-4 rounded-lg shadow-md ${darkMode ? 'bg-gray-800' : 'bg-gray-100'} hover:${darkMode ? 'bg-gray-700' : 'bg-gray-200'} transition-all duration-300`}
                            >
                                <Link
                                    to={`/company/${company.short_name}`}
                                    className={`text-xl font-medium ${darkMode ? 'text-blue-400 hover:text-blue-600' : 'text-blue-600 hover:text-blue-800'}`}
                                >
                                    <div className="flex justify-between">
                                        <span>{!company.name ? company.short_name : company.name}</span>
                                        <span className="text-sm text-gray-400">{company.short_name}</span>
                                    </div>
                                    <div className="text-lg mt-2">Stock Price: {company.price} MKD.</div> {/* Display stock price */}
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
