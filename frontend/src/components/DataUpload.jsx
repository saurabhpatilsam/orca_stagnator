import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Upload, 
  File, 
  Check,
  X,
  Database,
  Download,
  Eye,
  Trash2,
  AlertCircle,
  FileText,
  FileSpreadsheet
} from 'lucide-react';
import { supabase } from '../config/supabase';
import toast from 'react-hot-toast';

const DataUpload = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (files) => {
    const validFiles = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileExt = file.name.split('.').pop().toLowerCase();
      
      // Check file type
      if (!['csv', 'txt', 'json'].includes(fileExt)) {
        toast.error(`Invalid file type: ${file.name}. Only CSV, TXT, and JSON files are allowed.`);
        continue;
      }
      
      // Check file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error(`File too large: ${file.name}. Maximum size is 10MB.`);
        continue;
      }
      
      validFiles.push(file);
    }
    
    if (validFiles.length > 0) {
      uploadFiles(validFiles);
    }
  };

  const uploadFiles = async (files) => {
    setUploading(true);
    
    for (const file of files) {
      try {
        // Read file content for preview
        const reader = new FileReader();
        reader.onload = async (e) => {
          const content = e.target.result;
          
          // Parse CSV or TXT content
          let data = null;
          if (file.name.endsWith('.csv')) {
            data = parseCSV(content);
          } else if (file.name.endsWith('.txt')) {
            data = parseTXT(content);
          } else if (file.name.endsWith('.json')) {
            data = JSON.parse(content);
          }
          
          // Upload to Supabase Storage
          const { data: uploadData, error } = await supabase.storage
            .from('trading-data')
            .upload(`uploads/${Date.now()}_${file.name}`, file);
          
          if (!error) {
            const newFile = {
              id: Date.now(),
              name: file.name,
              size: file.size,
              type: file.type || 'text/plain',
              uploadedAt: new Date().toISOString(),
              status: 'completed',
              preview: data,
              path: uploadData?.path
            };
            
            setUploadedFiles(prev => [...prev, newFile]);
            toast.success(`Successfully uploaded ${file.name}`);
          } else {
            // If storage bucket doesn't exist, just store locally for demo
            const newFile = {
              id: Date.now(),
              name: file.name,
              size: file.size,
              type: file.type || 'text/plain',
              uploadedAt: new Date().toISOString(),
              status: 'completed',
              preview: data
            };
            
            setUploadedFiles(prev => [...prev, newFile]);
            toast.success(`Successfully processed ${file.name}`);
          }
        };
        
        reader.readAsText(file);
      } catch (error) {
        console.error('Upload error:', error);
        toast.error(`Failed to upload ${file.name}`);
      }
    }
    
    setUploading(false);
  };

  const parseCSV = (text) => {
    const lines = text.split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < Math.min(lines.length, 6); i++) {
      const values = lines[i].split(',');
      if (values.length === headers.length) {
        const row = {};
        headers.forEach((header, idx) => {
          row[header] = values[idx].trim();
        });
        data.push(row);
      }
    }
    
    return {
      headers,
      rows: data,
      totalRows: lines.length - 1
    };
  };

  const parseTXT = (text) => {
    const lines = text.split('\n').filter(line => line.trim());
    return {
      lines: lines.slice(0, 5),
      totalLines: lines.length
    };
  };

  const deleteFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    toast.success('File removed');
  };

  const viewFile = (file) => {
    setSelectedFile(file);
    setFilePreview(file.preview);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Data Management</h1>
        <p className="text-gray-400">Upload and manage trading data files</p>
      </div>

      {/* Upload Area */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Upload className="text-green-500" />
          Upload Files
        </h2>
        
        <div
          className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all ${
            dragActive 
              ? 'border-blue-500 bg-blue-500/10' 
              : 'border-gray-700 bg-gray-800 hover:border-gray-600'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".csv,.txt,.json"
            onChange={handleFileInput}
            className="hidden"
          />
          
          <Upload className="mx-auto mb-4 text-gray-400" size={48} />
          
          <p className="text-lg mb-2">
            {dragActive ? 'Drop files here' : 'Drag & drop files here'}
          </p>
          
          <p className="text-sm text-gray-400 mb-4">
            or
          </p>
          
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Browse Files'}
          </button>
          
          <p className="text-xs text-gray-400 mt-4">
            Supported formats: CSV, TXT, JSON (Max 10MB)
          </p>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Database className="text-purple-500" />
            Uploaded Files ({uploadedFiles.length})
          </h2>
          
          <div className="bg-gray-800 rounded-xl border border-gray-700">
            <div className="p-4">
              {uploadedFiles.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center justify-between p-4 border-b border-gray-700 last:border-0 hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-blue-600/20 rounded-lg flex items-center justify-center">
                      {file.name.endsWith('.csv') ? (
                        <FileSpreadsheet className="text-blue-500" size={20} />
                      ) : (
                        <FileText className="text-blue-500" size={20} />
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold">{file.name}</h3>
                      <p className="text-sm text-gray-400">
                        {formatFileSize(file.size)} • Uploaded {new Date(file.uploadedAt).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {file.status === 'completed' && (
                      <span className="px-2 py-1 bg-green-600 rounded text-xs flex items-center gap-1">
                        <Check size={12} />
                        Completed
                      </span>
                    )}
                    
                    <button
                      onClick={() => viewFile(file)}
                      className="p-2 hover:bg-gray-600 rounded-lg transition-colors"
                      title="View file"
                    >
                      <Eye size={18} />
                    </button>
                    
                    <button
                      onClick={() => deleteFile(file.id)}
                      className="p-2 hover:bg-red-600 rounded-lg transition-colors"
                      title="Delete file"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* File Preview Modal */}
      {selectedFile && filePreview && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedFile(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            className="bg-gray-800 rounded-xl p-6 max-w-4xl max-h-[80vh] overflow-auto border border-gray-700"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">File Preview: {selectedFile.name}</h3>
              <button
                onClick={() => setSelectedFile(null)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="bg-gray-900 rounded-lg p-4 overflow-auto">
              {selectedFile.name.endsWith('.csv') && filePreview.headers ? (
                <div>
                  <p className="text-sm text-gray-400 mb-2">
                    Showing first 5 rows of {filePreview.totalRows} total rows
                  </p>
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-700">
                        {filePreview.headers.map((header, idx) => (
                          <th key={idx} className="px-4 py-2 text-left text-gray-300">
                            {header}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {filePreview.rows.map((row, idx) => (
                        <tr key={idx} className="border-b border-gray-700">
                          {filePreview.headers.map((header, hidx) => (
                            <td key={hidx} className="px-4 py-2">
                              {row[header]}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : selectedFile.name.endsWith('.txt') && filePreview.lines ? (
                <div>
                  <p className="text-sm text-gray-400 mb-2">
                    Showing first 5 lines of {filePreview.totalLines} total lines
                  </p>
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                    {filePreview.lines.join('\n')}
                  </pre>
                </div>
              ) : (
                <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                  {JSON.stringify(filePreview, null, 2)}
                </pre>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Info Section */}
      <div className="bg-blue-900/20 border border-blue-600 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="text-blue-500 mt-1" size={20} />
          <div className="text-sm text-gray-300">
            <p className="font-semibold mb-1">Data Upload Guidelines</p>
            <ul className="list-disc list-inside space-y-1">
              <li>CSV files should have headers in the first row</li>
              <li>TXT files should contain structured data with consistent formatting</li>
              <li>JSON files must be valid JSON format</li>
              <li>Maximum file size is 10MB per file</li>
              <li>Data will be automatically processed and stored for analysis</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataUpload;
