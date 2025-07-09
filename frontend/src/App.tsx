import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ApplicationList } from './screens/ApplicationList';
import { AddApplication } from './screens/AddApplication';
import { ApplicationDetail } from './screens/ApplicationDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-xl font-bold text-gray-900">Job Tracker MVP</h1>
              <div className="text-sm text-gray-600">
                Powered by Temporal.io & Gemini AI
              </div>
            </div>
          </div>
        </nav>
        
        <main>
          <Routes>
            <Route path="/" element={<ApplicationList />} />
            <Route path="/applications/new" element={<AddApplication />} />
            <Route path="/applications/:id" element={<ApplicationDetail />} />
          </Routes>
        </main>
        
        <footer className="bg-white border-t mt-12">
          <div className="container mx-auto px-4 py-6">
            <div className="text-center text-gray-600 text-sm">
              <p>Job Application Tracker MVP - RSA Case Study Implementation</p>
              <p className="mt-1">Built with React, FastAPI, Temporal.io, and Gemini AI</p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;