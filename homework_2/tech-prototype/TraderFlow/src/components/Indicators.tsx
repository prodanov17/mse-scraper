import { useEffect, useState } from "react";
import { IndicatorData as IData } from "../utilities/types";

const Indicators = ({ companyId, darkMode }: { companyId: string; darkMode: boolean }) => {
    const [indicator, setIndicator] = useState('rsi'); // Default indicator
    const [indicatorData, setIndicatorData] = useState<IData[]>([]);
    const [companyDetails, setCompanyDetails] = useState<any>(null);

    const fetchIndicatorData = async () => {
        try {
            const response = await fetch(`http://localhost:5000/api/companies/${companyId}/indicators/${indicator}`);
            if (!response.ok) {
                throw new Error('Failed to fetch indicator data');
            }
            const data = await response.json();
            setIndicatorData(data.content);
        } catch (error) {
            console.error('Error fetching indicator data:', error);
        }
    };

    const fetchCompanyDetails = async () => {
        try {
            const response = await fetch(`http://localhost:5000/api/companies/${companyId}`);
            if (!response.ok) {
                throw new Error('Failed to fetch company details');
            }
            const data = await response.json();
            setCompanyDetails(data);
        } catch (error) {
            console.error('Error fetching company details:', error);
        }
    };

    useEffect(() => {
        fetchIndicatorData();
        fetchCompanyDetails();
    }, [indicator, companyId]);

    return (
        <div className={`p-4 ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}`}>
            {companyDetails && (
                <div className="mb-4">
                    <p className="text-lg">Price: {companyDetails.price} mkd</p>
                    <p className="text-lg">Predicted Price: {companyDetails.predicted_price} mkd</p>
                    <p className={`text-lg ${companyDetails.predicted_signal === 'buy' ? 'text-green-500' : companyDetails.predicted_signal === 'sell' ? 'text-red-500' : 'text-yellow-500'}`}>
                        Predicted Signal: {companyDetails.predicted_signal}
                    </p>
                </div>
            )}
            <h1 className="text-2xl mb-4">Indicators</h1>
            <select onChange={(e) => setIndicator(e.target.value)} value={indicator} className={`mb-4 p-2 border rounded ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-white text-gray-900'}`}>
                <option value="rsi">Relative Strength Index (RSI)</option>
                <option value="stoch">Stochastic Oscillator</option>
                <option value="williamsr">Williams %R</option>
                <option value="cci">Commodity Channel Index (CCI)</option>
                <option value="mfi">Money Flow Index (MFI)</option>
                <option value="ema">Exponential Moving Average (EMA)</option>
                <option value="sma">Simple Moving Average (SMA)</option>
                <option value="wma">Weighted Moving Average (WMA)</option>
            </select>

            <div>
                {indicatorData.length > 0 ? (
                    <table className={`min-w-full border border-gray-300 rounded-lg ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} overflow-hidden`}>
                        <thead className={`${darkMode ? 'bg-gray-700' : 'bg-gray-200'} rounded-t-lg`}>
                            <tr>
                                <th className="border px-4 py-2">Date</th>
                                <th className="border px-4 py-2">Close</th>
                                <th className="border px-4 py-2">Min</th>
                                <th className="border px-4 py-2">Max</th>
                                <th className="border px-4 py-2">Volume</th>
                                <th className="border px-4 py-2">Indicator</th>
                                <th className="border px-4 py-2">Signal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {indicatorData.map((entry, index) => (
                                <tr key={index} className="text-center">
                                    <td className="border px-4 py-2">{entry.date}</td>
                                    <td className="border px-4 py-2">{entry.close?.toFixed(2)}</td>
                                    <td className="border px-4 py-2">{entry.min?.toFixed(2)}</td>
                                    <td className="border px-4 py-2">{entry.max?.toFixed(2)}</td>
                                    <td className="border px-4 py-2">{entry.volume}</td>
                                    <td className="border px-4 py-2">{entry.indicator !== null ? entry.indicator : 'N/A'}</td>
                                    <td className={`border px-4 py-2 ${entry.signal === 'buy' ? 'text-green-500' : entry.signal === 'sell' ? 'text-red-500' : 'text-yellow-500'}`}>
                                        {entry.signal}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No indicator data available</p>
                )}
            </div>
        </div>
    );
};

export default Indicators;
