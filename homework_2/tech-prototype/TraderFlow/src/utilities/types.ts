export interface Company {
  short_name: string;
  name: string;
  price: number;
  price_change: number;
  stock_data?: Page<StockData>;
}

export interface IndicatorData {
  date: string;
  close: number;
  min: number;
  max: number;
  volume: number;
  indicator: number | null;
  signal: string;
}

export interface StockData {
  date: string;
  price: number;
  average_price: number;
  min: number;
  max: number;
  price_change: number;
  volume: number;
  best_turnover: number;
  total_turnover: number;
}

export interface PricePrediction {
  key: string;
  prediction: number;
}
export interface Sentiment {
  key: string;
  sentiment: string;
  score: number;
}

export interface Page<T> {
  content: T[];
  totalPages: number;
  totalElements: number;
  number: number;
  last: boolean;
  size: number;
}
