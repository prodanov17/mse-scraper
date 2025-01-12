import { useEffect, useState } from "react";
import IndicatorData from "./IndicatorData";
import { IndicatorData as IData } from "../utilities/types";

const Indicators = () => {
    const [indicator, setIndicator] = useState('sma');
    const [indicatorData, setIndicatorData] = useState<IData[]>([]);

    const fetchIndicatorData = async () => {
        // Fetch indicator data
        setIndicatorData([]);
    };

    useEffect(() => {
        // Fetch indicator data
        fetchIndicatorData();
    }, [indicator]);
    return (
        <div>
            <h1>Indicators</h1>
            <select onChange={(e) => setIndicator(e.target.value)}>
                <option value="sma">Simple Moving Average</option>
                <option value="ema">Exponential Moving Average</option>
                <option value="rsi">Relative Strength Index</option>
                <option value="macd">Moving Average Convergence Divergence</option>
            </select>

            <div>
                {/* Display selected indicator */}
                <IndicatorData data={indicatorData} />
            </div>

        </div>
    );

}

export default Indicators;
