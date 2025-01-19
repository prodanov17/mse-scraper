import { useCallback, useEffect, useState } from "react";
import { IndicatorData as IData } from "../utilities/types";
import api from "../utilities/fetching";
import IndicatorData from "./IndicatorData";
import ApiError from "../utilities/apierror";

const Indicators = ({ companyId, darkMode }: { companyId: string; darkMode: boolean }) => {
    const [indicator, setIndicator] = useState('rsi'); // Default indicator
    const [indicatorData, setIndicatorData] = useState<IData[]>([]);
    const [error, setError] = useState<ApiError | null>(null);

    const fetchIndicatorData = useCallback(async (indicator: string) => {
        try {
            const response = await api.get(`companies/${companyId}/indicators/${indicator}`) as IData[];
            setIndicatorData(response);
        } catch (error) {
            if (error instanceof Error) {
                setError(new ApiError(500, error.message, 'Failed to fetch indicator data'));
            }
            console.error('Error fetching indicator data:', error);
        }
    }, [companyId]);

    useEffect(() => {
        fetchIndicatorData(indicator);
    }, [indicator, companyId, fetchIndicatorData]);

    if (error) {
        return (
            <div className="p-4 bg-red-100 text-red-900">
                <h2 className="text-xl">Error fetching indicator data</h2>
                <p>{error.message}</p>
            </div>
        );
    }

    return (
        <div className={`p-4 ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}`}>
            <h1 className="text-2xl mb-4">Indicators</h1>
            
            <select 
                onChange={(e) => setIndicator(e.target.value)} 
                value={indicator}
                className={`mb-4 p-2 border rounded ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-white text-gray-900'}`}
            >
                <option value="rsi">Relative Strength Index (RSI)</option>
                <option value="stoch">Stochastic Oscillator</option>
                <option value="williamsr">Williams %R</option>
                <option value="cci">Commodity Channel Index (CCI)</option>
                <option value="mfi">Money Flow Index (MFI)</option>
                <option value="ema">Exponential Moving Average (EMA)</option>
                <option value="sma">Simple Moving Average (SMA)</option>
                <option value="wma">Weighted Moving Average (WMA)</option>
            </select>

            {indicatorData && indicatorData.length > 0 ? (
                <IndicatorData data={indicatorData} darkMode={darkMode} />
            ) : (
                <p>No indicator data available</p>
            )}
        </div>
    );
};

export default Indicators;
