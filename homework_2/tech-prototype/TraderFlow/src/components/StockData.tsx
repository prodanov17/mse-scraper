import { StockData } from '../utilities/types';

const StockDataTable = ({ stockData }: { stockData: StockData[] }) => {
    return (
        <table className="min-w-full table-auto border border-gray-300 rounded-lg overflow-hidden">
            <thead className="bg-gray-200">
                <tr>
                    <th className="px-4 py-2">Date</th>
                    <th className="px-4 py-2">Price</th>
                    <th className="px-4 py-2">Volume</th>
                    <th className="px-4 py-2">Price Change</th>
                </tr>
            </thead>
            <tbody>
                {stockData.map((data, index) => (
                    <tr key={index} className="border-b border-gray-300">
                        <td className="px-4 py-2">{data.date}</td>
                        <td className="px-4 py-2">{data.price}</td>
                        <td className="px-4 py-2">{data.volume}</td>
                        <td className="px-4 py-2">{data.price_change}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default StockDataTable;
