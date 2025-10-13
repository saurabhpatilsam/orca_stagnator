import React, { useState } from 'react';
import { Upload, Database, Server, CheckCircle, XCircle, Loader2, FileText, Clock, TrendingUp } from 'lucide-react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [instrument, setInstrument] = useState('ES');
  const [hasHeader, setHasHeader] = useState(false);
  const [skipDuplicates, setSkipDuplicates] = useState(false);
  const [supabaseTarget, setSupabaseTarget] = useState('selfhosted');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
    setResult(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.csv') || droppedFile.name.endsWith('.txt'))) {
      setFile(droppedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please drop a TXT or CSV file');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);
    setProgress({ current: 0, total: 100, message: 'Preparing upload...' });

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('instrument', instrument);
      formData.append('has_header', hasHeader);
      formData.append('skip_duplicates', skipDuplicates);
      formData.append('supabase_target', supabaseTarget);

      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = Math.round((e.loaded / e.total) * 100);
          setProgress({
            current: percentComplete,
            total: 100,
            message: `Uploading... ${percentComplete}%`
          });
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          setResult(response);
          setProgress(null);
        } else {
          const errorData = JSON.parse(xhr.responseText);
          setError(errorData.detail || 'Upload failed');
          setProgress(null);
        }
        setUploading(false);
      });

      xhr.addEventListener('error', () => {
        setError('Network error occurred');
        setProgress(null);
        setUploading(false);
      });

      xhr.open('POST', '/api/upload-tick-data');
      xhr.timeout = 900000;
      xhr.send(formData);

    } catch (err) {
      setError(err.message || 'Upload failed');
      setProgress(null);
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4">
            <div className="bg-black p-3 rounded-xl">
              <Database className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Tick Data Upload</h1>
              <p className="text-gray-600 mt-1">Upload ES/NQ tick-by-tick data to Supabase</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column - Upload Configuration */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Supabase Target Selection */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Select Database</h2>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setSupabaseTarget('selfhosted')}
                  className={`p-6 rounded-xl border-2 transition-all duration-200 ${
                    supabaseTarget === 'selfhosted'
                      ? 'border-black bg-black text-white shadow-lg'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Server className="w-8 h-8 mb-3 mx-auto" />
                  <div className="font-semibold">MagicPitch</div>
                  <div className="text-sm opacity-75 mt-1">Self-Hosted</div>
                </button>
                <button
                  onClick={() => setSupabaseTarget('cloud')}
                  className={`p-6 rounded-xl border-2 transition-all duration-200 ${
                    supabaseTarget === 'cloud'
                      ? 'border-black bg-black text-white shadow-lg'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Database className="w-8 h-8 mb-3 mx-auto" />
                  <div className="font-semibold">Supabase</div>
                  <div className="text-sm opacity-75 mt-1">Cloud Hosted</div>
                </button>
              </div>
            </div>

            {/* File Upload */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Upload File</h2>
              <div
                className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
                  file
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 bg-gray-50 hover:border-gray-400 hover:bg-gray-100'
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
              >
                <input
                  type="file"
                  accept=".txt,.csv"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-input"
                />
                <label htmlFor="file-input" className="cursor-pointer">
                  {file ? (
                    <div className="space-y-3">
                      <FileText className="w-16 h-16 mx-auto text-green-600" />
                      <div>
                        <p className="text-lg font-semibold text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-600 mt-1">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          setFile(null);
                        }}
                        className="text-sm text-gray-600 hover:text-gray-900 underline"
                      >
                        Change file
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Upload className="w-16 h-16 mx-auto text-gray-400" />
                      <div>
                        <p className="text-lg font-medium text-gray-700">Drop your file here</p>
                        <p className="text-sm text-gray-500 mt-1">or click to browse</p>
                      </div>
                      <p className="text-xs text-gray-400">Supports TXT and CSV files</p>
                    </div>
                  )}
                </label>
              </div>
            </div>

            {/* Configuration Options */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Configuration</h2>
              <div className="space-y-4">
                
                {/* Instrument */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Instrument
                  </label>
                  <select
                    value={instrument}
                    onChange={(e) => setInstrument(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all"
                  >
                    <option value="ES">ES - E-mini S&P 500</option>
                    <option value="NQ">NQ - E-mini NASDAQ-100</option>
                  </select>
                </div>

                {/* Options */}
                <div className="space-y-3 pt-4">
                  <label className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-all">
                    <input
                      type="checkbox"
                      checked={hasHeader}
                      onChange={(e) => setHasHeader(e.target.checked)}
                      className="w-5 h-5 text-black border-gray-300 rounded focus:ring-black"
                    />
                    <span className="text-sm font-medium text-gray-700">File has header row</span>
                  </label>

                  <label className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-all">
                    <input
                      type="checkbox"
                      checked={skipDuplicates}
                      onChange={(e) => setSkipDuplicates(e.target.checked)}
                      className="w-5 h-5 text-black border-gray-300 rounded focus:ring-black"
                    />
                    <span className="text-sm font-medium text-gray-700">Skip duplicate rows</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full bg-black text-white py-4 px-6 rounded-xl font-semibold text-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center space-x-3"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <Upload className="w-6 h-6" />
                  <span>Upload to {supabaseTarget === 'selfhosted' ? 'MagicPitch' : 'Supabase Cloud'}</span>
                </>
              )}
            </button>

          </div>

          {/* Right Column - Status & Info */}
          <div className="space-y-6">
            
            {/* Progress */}
            {progress && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Upload Progress</h3>
                <div className="space-y-4">
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-black h-full transition-all duration-300 rounded-full"
                      style={{ width: `${progress.current}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">{progress.message}</span>
                    <span className="font-semibold text-gray-900">{progress.current}%</span>
                  </div>
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
                <div className="flex items-start space-x-3">
                  <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-red-900">Upload Failed</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Success Result */}
            {result && result.success && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  <h3 className="font-semibold text-gray-900">Upload Successful</h3>
                </div>
                
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Uploaded</div>
                      <div className="text-2xl font-bold text-green-600">
                        {result.uploaded_rows?.toLocaleString() || 0}
                      </div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Skipped</div>
                      <div className="text-2xl font-bold text-gray-600">
                        {result.skipped_rows?.toLocaleString() || 0}
                      </div>
                    </div>
                  </div>

                  {result.date_range && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <Clock className="w-4 h-4" />
                        <span>
                          {result.date_range.start} → {result.date_range.end}
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="pt-3 border-t border-gray-200">
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Table:</span> {result.table}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      <span className="font-medium">Duration:</span> {result.duration}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Info Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Quick Guide</span>
              </h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start space-x-2">
                  <span className="text-black font-bold">1.</span>
                  <span>Select your Supabase database (MagicPitch or Cloud)</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-black font-bold">2.</span>
                  <span>Choose your instrument (ES or NQ)</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-black font-bold">3.</span>
                  <span>Upload your tick data file</span>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="text-black font-bold">4.</span>
                  <span>Monitor the upload progress</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
