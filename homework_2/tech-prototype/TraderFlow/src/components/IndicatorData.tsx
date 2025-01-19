import { IndicatorData as IData } from "../utilities/types";

const resolveSignalColor = (signal: string) => {
    switch (signal.toUpperCase()) {
        case 'BUY':
            return 'text-green-500';  // Green for buy signal
        case 'SELL':
            return 'text-red-500';    // Red for sell signal
        default:
            return 'text-orange-500'; // Default (neutral) color for other signals
    }
}

const IndicatorData = ({ data: indicator_data, darkMode }: { data: IData[] | null, darkMode: boolean }) => {
    return (
        <div
            className={`rounded-lg p-4 overflow-hidden overflow-x-auto scroll-hidden ${
                darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
            }`}
        >
            <h2 className="text-2xl mt-6 mb-4">Stock</h2>
            {indicator_data && indicator_data.length > 0 ? (
                <table
                    className={`table-auto w-full text-sm text-left ${
                        darkMode ? 'bg-gray-700 text-white' : 'bg-white text-gray-900'
                    }`}
                >
                    <thead className="border-b">
                        <tr>
                            <th className="px-4 py-2">Date</th>
                            <th className="px-4 py-2">Close</th>
                            <th className="px-4 py-2">Max</th>
                            <th className="px-4 py-2">Min</th>
                            <th className="px-4 py-2">Indicator</th>
                            <th className="px-4 py-2">Signal</th>
                            <th className="px-4 py-2">Volume</th>
                        </tr>
                    </thead>
                    <tbody>
                        {indicator_data.map((entry, index) => (
                            <tr
                                key={index}
                                className={`border-b ${
                                    darkMode ? 'bg-gray-800' : 'bg-white'
                                }`}
                            >
                                <td className="px-4 py-2">{entry.date}</td>
                                <td className="px-4 py-2">{entry.close?.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.max?.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.min?.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.indicator || "N/A"}</td>
                                <td className={`px-4 py-2 ${resolveSignalColor(entry.signal)}`}>
                                    {entry.signal}
                                </td>
                                <td className="px-4 py-2">{entry.volume}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No stock history available</p>
            )}
        </div>
    );
}

export default IndicatorData;
