import { Page, StockData as SData } from "../utilities/types";

const StockDataTable = ({
    stockData: stock_data,
}: {
    stockData: Page<SData> | null;
}) => {
    return (
        <div className="bg-white rounded-lg p-4 overflow-hidden overflow-x-auto scroll-hidden">
            {/* Stock History */}
            <h2 className="text-2xl mt6 mb-4">Stock History</h2>
            {stock_data && stock_data.content && stock_data.content.length > 0 ? (
                <table className="table-auto w-full text-sm text-left">
                    <thead className="border-b">
                        <tr>
                            <th className="px-4 py-2">Date</th>
                            <th className="px-4 py-2">Last Trade Price</th>
                            <th className="px-4 py-2">Max</th>
                            <th className="px-4 py-2">Min</th>
                            <th className="px-4 py-2">Avg.</th>
                            <th className="px-4 py-2">Price % Chg.</th>
                            <th className="px-4 py-2">Volume</th>
                            <th className="px-4 py-2">Turnover in BEST (Denars)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {stock_data.content.map((entry, index) => (
                            <tr key={index} className="border-b">
                                <td className="px-4 py-2">{entry.date}</td>
                                <td className="px-4 py-2">{entry.price.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.max.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.min.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.average_price.toFixed(2)}</td>
                                <td className="px-4 py-2">{entry.price_change?.toFixed(2) || "0.00"}%</td>
                                <td className="px-4 py-2">{entry.volume}</td>
                                <td className="px-4 py-2">{entry.best_turnover.toLocaleString()}</td>
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

// <button
// onClick={() => changePage(false)}
// className="bg-blue-500 text-white p-2 rounded-md focus:outline-none hover:bg-blue-700"
// >
// Previous
// </button>
// <button
// onClick={() => changePage(true)}
// className="bg-blue-500 text-white p-2 rounded-md focus:outline-none hover:bg-blue-700"
// >
// Next
// </button>
export default StockDataTable;
