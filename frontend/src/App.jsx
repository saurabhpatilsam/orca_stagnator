// Dual Supabase Support - Updated 2025-10-13
import React, { useState } from 'react';
import { Upload, Database, CheckCircle, XCircle, Loader, AlertCircle } from 'lucide-react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [instrument, setInstrument] = useState('ES');
  const [hasHeader, setHasHeader] = useState(false);
  const [skipDuplicates, setSkipDuplicates] = useState(false); // Disabled for faster uploads
  const [supabaseTarget, setSupabaseTarget] = useState('selfhosted'); // 'selfhosted' or 'cloud'
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
      setError('Please drop a TXT file');
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

      // Use XMLHttpRequest for upload progress
      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = Math.round((e.loaded / e.total) * 100);
          setProgress({
            current: percentComplete,
            total: 100,
            message: `Uploading file... ${percentComplete}%`
          });
        }
      });

      // When upload completes, switch to processing message
      xhr.upload.addEventListener('load', () => {
        setProgress({ 
          current: 100, 
          total: 100, 
          message: 'Upload complete! Processing file on server...' 
        });
      });

      // Handle completion
      const uploadPromise = new Promise((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const data = JSON.parse(xhr.responseText);
              resolve(data);
            } catch (err) {
              reject(new Error('Invalid response from server'));
            }
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText);
              reject(new Error(errorData.error || `Upload failed with status ${xhr.status}`));
            } catch (err) {
              reject(new Error(`Upload failed with status ${xhr.status}`));
            }
          }
        };

        xhr.onerror = () => reject(new Error('Network error occurred'));
        xhr.ontimeout = () => reject(new Error('Upload timed out - file may be too large'));

        xhr.open('POST', '/api/upload-tick-data');
        xhr.timeout = 900000; // 15 minutes timeout for large files
        xhr.send(formData);
      });

      const data = await uploadPromise;

      if (data.success) {
        setResult(data);
        setProgress(null);
      } else {
        setError(data.error || 'Upload failed');
        setProgress(null);
      }
    } catch (err) {
      setError(`Upload error: ${err.message}`);
      setProgress(null);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <div className="header">
          <Database className="header-icon" size={40} />
          <h1>Supabase Tick Data Upload</h1>
          <p className="subtitle">Upload ES/NQ tick-by-tick data to Supabase</p>
        </div>

        {/* Supabase Target Selection */}
        <div className="supabase-selector">
          <label className="selector-label">Select Supabase Database:</label>
          <div className="selector-buttons">
            <button
              className={`selector-btn ${supabaseTarget === 'selfhosted' ? 'active' : ''}`}
              onClick={() => setSupabaseTarget('selfhosted')}
            >
              <Database size={20} />
              MagicPitch Supabase
            </button>
            <button
              className={`selector-btn ${supabaseTarget === 'cloud' ? 'active' : ''}`}
              onClick={() => setSupabaseTarget('cloud')}
            >
              <Upload size={20} />
              Supabase Hosted
            </button>
          </div>
        </div>

        {/* Upload Area */}
        <div className="upload-section">
          <div
            className={`dropzone ${file ? 'has-file' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <Upload className="dropzone-icon" size={48} />
            {file ? (
              <div className="file-info">
                <p className="file-name">{file.name}</p>
                <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            ) : (
              <>
                <p className="dropzone-text">Drag & drop your TXT file here</p>
                <p className="dropzone-subtext">or click to browse</p>
              </>
            )}
            <input
              type="file"
              accept=".txt"
              onChange={handleFileChange}
              className="file-input"
            />
          </div>
        </div>

        {/* Configuration */}
        <div className="config-section">
          <h3>Upload Configuration</h3>
          
          <div className="config-grid">
            {/* Instrument Selection */}
            <div className="config-item">
              <label>Instrument</label>
              <select
                value={instrument}
                onChange={(e) => setInstrument(e.target.value)}
                className="select-input"
              >
                <option value="ES">ES (E-mini S&P 500)</option>
                <option value="NQ">NQ (E-mini NASDAQ)</option>
              </select>
            </div>

            {/* Has Header */}
            <div className="config-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={hasHeader}
                  onChange={(e) => setHasHeader(e.target.checked)}
                  className="checkbox-input"
                />
                <span>File has header row</span>
              </label>
            </div>

            {/* Skip Duplicates */}
            <div className="config-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={skipDuplicates}
                  onChange={(e) => setSkipDuplicates(e.target.checked)}
                  className="checkbox-input"
                />
                <span>Skip duplicate rows</span>
              </label>
            </div>
          </div>
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={uploading || (!file && !filePath)}
          className="upload-btn"
        >
          {uploading ? (
            <>
              <Loader className="spin" size={20} />
              Uploading...
            </>
          ) : (
            <>
              <Upload size={20} />
              Upload to Supabase
            </>
          )}
        </button>

        {/* Progress */}
        {progress && (
          <div className="progress-section">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: progress.total > 0 ? `${(progress.current / progress.total) * 100}%` : '0%'
                }}
              />
            </div>
            <p className="progress-text">{progress.message}</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="alert alert-error">
            <XCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Success Result */}
        {result && (
          <div className="result-section">
            <div className="alert alert-success">
              <CheckCircle size={20} />
              <span>Upload completed successfully!</span>
            </div>
            
            <div className="stats-grid">
              <div className="stat-card">
                <p className="stat-label">Total Rows</p>
                <p className="stat-value">{result.total_rows?.toLocaleString()}</p>
              </div>
              <div className="stat-card">
                <p className="stat-label">Uploaded</p>
                <p className="stat-value success">{result.uploaded_rows?.toLocaleString()}</p>
              </div>
              <div className="stat-card">
                <p className="stat-label">Duplicates Skipped</p>
                <p className="stat-value warning">{result.skipped_rows?.toLocaleString()}</p>
              </div>
              <div className="stat-card">
                <p className="stat-label">Errors</p>
                <p className="stat-value error">{result.error_rows?.toLocaleString()}</p>
              </div>
            </div>

            {result.date_range && (
              <div className="date-range">
                <AlertCircle size={16} />
                <span>
                  Date Range: {result.date_range.start} to {result.date_range.end}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Info Section */}
        <div className="info-section">
          <h4>📋 Supported File Formats</h4>
          <ul>
            <li>TXT files with comma, tab, or semicolon separators</li>
            <li>Files with or without header rows</li>
            <li>Custom timestamp formats (YYYYMMDD HHMMSS)</li>
            <li>Columns: timestamp, bid, ask, last, volume</li>
          </ul>
          
          <h4>✅ Features</h4>
          <ul>
            <li>Automatic duplicate detection (exact row matching)</li>
            <li>Batch processing for large files (millions of rows)</li>
            <li>Multiple ticks at same timestamp preserved</li>
            <li>Real-time progress tracking</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
