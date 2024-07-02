import React, { useState } from 'react';
import Home from './components/Home';
import './App.css';

function App() {
  const [selectedOption, setSelectedOption] = useState('video');

  return (
    <div className="min-h-screen pt-1 bg-gradient-to-br from-indigo-600 to-purple-700">
      <header className="bg-white rounded-lg shadow-lg p-6 pb-4 mx-auto max-w-3xl my-8">
        <h1 className="text-4xl font-bold text-center text-indigo-900">
          Music Bridge - Spotify Music Downloader
        </h1>
        <div className="flex justify-center mt-5">
          <div className="flex space-x-2 border-[3px] border-purple-400 rounded-xl select-none w-1/2">
            <label className="radio flex flex-grow items-center justify-center rounded-lg p-1 cursor-pointer">
              <input
                type="radio"
                name="radio"
                value="video"
                className="peer hidden"
                checked={selectedOption === 'video'}
                onChange={() => setSelectedOption('video')}
              />
              <span className="tracking-widest peer-checked:bg-gradient-to-r peer-checked:from-[blueviolet] peer-checked:to-[violet] peer-checked:text-white text-gray-700 p-2 rounded-lg transition duration-150 ease-in-out hover:scale-105">
                Video Download
              </span>
            </label>
            <label className="radio flex flex-grow items-center justify-center rounded-lg p-1 cursor-pointer">
              <input
                type="radio"
                name="radio"
                value="audio"
                className="peer hidden"
                checked={selectedOption === 'audio'}
                onChange={() => setSelectedOption('audio')}
              />
              <span className="tracking-widest peer-checked:bg-gradient-to-r peer-checked:from-[blueviolet] peer-checked:to-[violet] peer-checked:text-white text-gray-700 p-2 rounded-lg transition duration-150 ease-in-out hover:scale-105">
                Audio Download
              </span>
            </label>
          </div>
        </div>
      </header>
      <main className="bg-white rounded-lg shadow-lg p-8 mx-auto max-w-3xl">
        <Home selectedOption={selectedOption} />
      </main>
      <footer className="bg-white rounded-lg shadow-lg p-4 mx-auto max-w-3xl mt-8 text-center text-gray-600">
        &copy; {new Date().getFullYear()} Music Bridge. All rights reserved.
      </footer>
    </div>
  );
}

export default App;
