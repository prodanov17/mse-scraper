import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './components/HomePage';
import CompanyDetails from './components/CompanyDetails';

const App = () => {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/company/:companyId" element={<CompanyDetails />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
