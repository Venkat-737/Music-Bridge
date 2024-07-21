import React, { useState } from 'react';
import { CloudDownloadIcon, CheckCircleIcon, ExclamationIcon, ArrowRightIcon } from '@heroicons/react/solid';
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function Home({ selectedOption }) {
  const [url, setUrl] = useState('');
  const [showAlert, setShowAlert] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [quality, setQuality] = useState('1080px');

  const handleDownloadClick = async () => {
    setIsLoading(true);
    setShowAlert(false);
    setStatus('');
    setErrorMessage('');

    try {
      const response = await fetch('http://localhost:5000/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, output_path: 'C:/VideoSongsOutput', quality, type: selectedOption }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = 'downloaded_file'; // You might want to get the actual filename from the server
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        setStatus('success');
        setShowAlert(true);
      } else {
        const errorData = await response.json();
        handleErrors(errorData);
      }
    } catch (error) {
      setErrorMessage('An error occurred during the download. Please try again later.');
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleErrors = (error) => {
    if (error.message.includes('invalid id')) {
      setErrorMessage('Invalid Spotify URL. Please check the URL and try again.');
    } else {
      setErrorMessage(error.message || 'Download failed. Please check the URL and try again.');
    }
    setStatus('error');
    console.error(error.message || 'Download failed.');
  };

  return (
    <div>
      {selectedOption === 'video' ? (
        <>
          <div className="mb-6">
            <label htmlFor="url" className="flex justify-between text-gray-700 font-bold mb-2">
              Enter Spotify Song URL or Playlist URL
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="border shadow-xl w-32 mb-2 gap-5">
                    <ArrowRightIcon className='w-4 h-3'/> {quality}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuLabel>Select Quality</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuRadioGroup value={quality} onValueChange={setQuality}>
                    <DropdownMenuRadioItem value="Highest">Highest</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="1080px">1080px</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="720px">720px</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="480px">480px</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="360px">360px</DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="Lowest">Lowest</DropdownMenuRadioItem>
                  </DropdownMenuRadioGroup>
                </DropdownMenuContent>
              </DropdownMenu>
            </label>
            <input
              type="text"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="shadow appearance-none border rounded w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="https://open.spotify.com/..."
            />
          </div>
        </>
      ) : (
        <>
          <div className="mb-6">
            <label htmlFor="url" className="flex justify-between text-gray-700 font-bold mb-4">
              Enter Spotify Song URL or Playlist URL
            </label>
            <input
              type="text"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="shadow appearance-none border rounded w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="https://open.spotify.com/..."
            />
          </div>
        </>
      )}

      <div className="flex justify-center">
        <button
          onClick={handleDownloadClick}
          disabled={isLoading}
          className={`bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-full focus:outline-none focus:shadow-outline transition duration-300 ease-in-out flex items-center ${
            isLoading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isLoading ? (
            <span className="flex items-center">
              <CloudDownloadIcon className="h-6 w-6 animate-spin mr-2" />
              Downloading...
            </span>
          ) : (
            <span className="flex items-center">
              <CloudDownloadIcon className="h-6 w-6 mr-2" />
              Download {selectedOption === 'video' ? 'Video' : 'Audio'}
            </span>
          )}
        </button>
      </div>

      {status === 'success' && (
        <div className="mt-6 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg flex items-center">
          <CheckCircleIcon className="h-6 w-6 mr-2" />
          <span className="font-semibold mr-2">Success!</span>
          <span>Download has completed. Check your downloads folder.</span>
        </div>
      )}

      {status === 'error' && (
        <div className="mt-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg flex items-center">
          <ExclamationIcon className="h-6 w-6 mr-2" />
          <span className="font-semibold mr-2">Error!</span>
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}

export default Home;
