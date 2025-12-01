import React, { useState } from 'react';
import './App.css';
import { LanguageProvider } from './context/LanguageContext';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import HomePage from './components/HomePage';
import ConverterPage from './components/ConverterPage';
import PortfolioPage from './components/PortfolioPage';

function App() {
  const [activeTab, setActiveTab] = useState('home');

  return (
    <LanguageProvider>
      <div className="App min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-[480px] mx-auto">
          {activeTab === 'home' && <HomePage />}
          {activeTab === 'converter' && <ConverterPage />}
          {activeTab === 'portfolio' && <PortfolioPage />}
        </main>
        <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>
    </LanguageProvider>
  );
}

export default App;