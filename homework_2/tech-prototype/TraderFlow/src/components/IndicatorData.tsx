import { IndicatorData as IData } from "../utilities/types";


const resolveSignalColor = (signal: string) => {
    switch (signal.toUpperCase()) {
        case 'BUY':
            return 'text-green-500';
        case 'SELL':
            return 'text-red-500';
        default:
            return 'text-orange-500';
    }
}

const IndicatorData = ({ data: indicator_data }: { data: IData[] | null }) => {
    return (
        <>
            <h2 className="text-2xl mt-6 mb-4">Stock</h2>
            {indicator_data && indicator_data.length > 0 ? (
                <table className="table-auto w-full text-sm text-left">
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
                            <tr key={index} className="border-b">
                                <td className="px-4 py-2">{entry.date}</td>
                                <td className="px-4 py-2">{entry.close?.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.max?.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.min?.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.indicator || "N/A"}</td>
                                <td className={`px-4 py-2 ${resolveSignalColor(entry.signal)}`}>{entry.signal}</td>
                                <td className="px-4 py-2">{entry.volume}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No stock history available</p>
            )}

        </>
    );
}

export default IndicatorData;
