import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { QuickPredict } from './pages/QuickPredict/QuickPredict';
import { BatchUpload } from './pages/BatchUpload/BatchUpload';
import { History } from './pages/History/History';
import { Analytics } from './pages/Analytics/Analytics';
import { ReviewQueue } from './pages/ReviewQueue/ReviewQueue';
import { Settings } from './pages/Settings/Settings';
import './App.css';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<QuickPredict />} />
          <Route path="/batch" element={<BatchUpload />} />
          <Route path="/history" element={<History />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/review" element={<ReviewQueue />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
};

export default App;
