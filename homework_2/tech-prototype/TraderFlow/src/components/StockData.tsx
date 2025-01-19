import { useState } from "react";
import { Page, StockData as SData } from "../utilities/types";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register necessary chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const StockDataTable = ({
  stockData,
  darkMode,
}: {
  stockData: Page<SData> | null;
  darkMode: boolean;
}) => {
  // Date range state
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  // Filter stock data based on the selected date range
  const filterDataByDate = (data: SData[]) => {
    if (!startDate || !endDate) return data; // If no date range is selected, return all data

    const start = new Date(startDate);
    const end = new Date(endDate);

    return data.filter((entry) => {
      const entryDate = new Date(entry.date);
      return entryDate >= start && entryDate <= end;
    });
  };

  const filteredData = stockData ? filterDataByDate(stockData.content) : [];

  // Prepare chart data
  const chartData = {
    labels: filteredData.map((entry) => entry.date), // Dates on X-axis
    datasets: [
      {
        label: "Last Trade Price",
        data: filteredData.map((entry) => entry.price), // Stock price data
        borderColor: "rgba(75, 192, 192, 1)", // Line color
        backgroundColor: "rgba(75, 192, 192, 0.2)", // Fill color
        fill: true,
        tension: 0.4,
      },
      {
        label: "Max Price",
        data: filteredData.map((entry) => entry.max),
        borderColor: "rgba(255, 99, 132, 1)",
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        fill: true,
        tension: 0.4,
      },
      {
        label: "Min Price",
        data: filteredData.map((entry) => entry.min),
        borderColor: "rgba(153, 102, 255, 1)",
        backgroundColor: "rgba(153, 102, 255, 0.2)",
        fill: true,
        tension: 0.4,
      },
    ],
  };

  return (
    <div
      className={`rounded-lg p-4 overflow-hidden overflow-x-auto scroll-hidden ${
        darkMode ? "bg-gray-800 text-white" : "bg-white text-gray-900"
      }`}
    >
      {/* Date Range Inputs */}
      <div className="flex space-x-4 mb-4">
        <div className="flex flex-col">
          <label
            htmlFor="startDate"
            className={`text-sm mb-2 ${darkMode ? "text-gray-300" : "text-gray-700"}`}
          >
            Start Date
          </label>
          <input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className={`p-2 border rounded ${
              darkMode
                ? "bg-gray-700 text-white border-gray-600"
                : "bg-white text-gray-900 border-gray-300"
            }`}
          />
        </div>

        <div className="flex flex-col">
          <label
            htmlFor="endDate"
            className={`text-sm mb-2 ${darkMode ? "text-gray-300" : "text-gray-700"}`}
          >
            End Date
          </label>
          <input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className={`p-2 border rounded ${
              darkMode
                ? "bg-gray-700 text-white border-gray-600"
                : "bg-white text-gray-900 border-gray-300"
            }`}
          />
        </div>
      </div>

      {/* Stock History */}
      <h2 className="text-2xl mt-6 mb-4">Stock History</h2>
      {filteredData.length > 0 ? (
        <>
          {/* Chart */}
          <div className="mb-6">
            <Line
              data={chartData}
              options={{
                responsive: true,
                plugins: {
                  title: {
                    display: true,
                    text: "Stock Price Trends",
                    color: darkMode ? "white" : "black", // Adjust title color for dark mode
                  },
                  tooltip: {
                    mode: "index",
                    intersect: false,
                  },
                },
                scales: {
                  x: {
                    title: {
                      display: true,
                      text: "Date",
                      color: darkMode ? "white" : "black", // Adjust axis label color for dark mode
                    },
                  },
                  y: {
                    title: {
                      display: true,
                      text: "Price",
                      color: darkMode ? "white" : "black", // Adjust axis label color for dark mode
                    },
                  },
                },
              }}
            />
          </div>

          {/* Stock History Table */}
          <table
            className={`table-auto w-full text-sm text-left ${
              darkMode ? "bg-gray-700 text-white" : "bg-white text-gray-900"
            }`}
          >
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
              {filteredData.map((entry, index) => (
                <tr
                  key={index}
                  className={`border-b ${darkMode ? "bg-gray-800" : "bg-white"}`}
                >
                  <td className="px-4 py-2">{entry.date}</td>
                  <td className="px-4 py-2">{entry.price.toFixed(2)}</td>
                  <td className="px-4 py-2">{entry.max.toFixed(2)}</td>
                  <td className="px-4 py-2">{entry.min.toFixed(2)}</td>
                  <td className="px-4 py-2">{entry.average_price.toFixed(2)}</td>
                  <td className="px-4 py-2">
                    {entry.price_change?.toFixed(2) || "0.00"}%
                  </td>
                  <td className="px-4 py-2">{entry.volume}</td>
                  <td className="px-4 py-2">
                    {entry.best_turnover.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        <p>No stock history available</p>
      )}
    </div>
  );
};

export default StockDataTable;
