import React, { useState } from 'react';

const DataEditor = () => {
  const [selectedFormat, setSelectedFormat] = useState('json'); // 'json', 'csv', 'table'
  const [dataInput, setDataInput] = useState('');

  const handleCreateDataset = async () => {
    // This will eventually send data to the backend
    console.log('Creating dataset:', { selectedFormat, dataInput });
    // TODO: Implement actual API call to /api/create-dataset-from-editor
    alert('Dataset creation initiated. Check console for data.');
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Data Editor</h2>

      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Select Data Format:
        </label>
        <div className="flex space-x-4">
          <button
            className={`px-4 py-2 rounded ${
              selectedFormat === 'json' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
            }`}
            onClick={() => setSelectedFormat('json')}
          >
            JSON
          </button>
          <button
            className={`px-4 py-2 rounded ${
              selectedFormat === 'csv' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
            }`}
            onClick={() => setSelectedFormat('csv')}
          >
            CSV
          </button>
          <button
            className={`px-4 py-2 rounded ${
              selectedFormat === 'table' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
            }`}
            onClick={() => setSelectedFormat('table')}
          >
            Table (for XLSX/CSV)
          </button>
        </div>
      </div>

      <div className="mb-4">
        {selectedFormat === 'json' && (
          <textarea
            className="w-full p-2 border rounded resize-y"
            rows="10"
            placeholder="Enter JSON data here..."
            value={dataInput}
            onChange={(e) => setDataInput(e.target.value)}
          ></textarea>
        )}
        {selectedFormat === 'csv' && (
          <textarea
            className="w-full p-2 border rounded resize-y"
            rows="10"
            placeholder="Enter CSV data here..."
            value={dataInput}
            onChange={(e) => setDataInput(e.target.value)}
          ></textarea>
        )}
        {selectedFormat === 'table' && (
          <div className="border p-2 rounded bg-gray-50 h-64 overflow-auto">
            <p className="text-gray-500">
              Table editor goes here. For now, you can switch to CSV to input table-like data.
              Boolean options will be integrated into the table editor.
            </p>
            {/* TODO: Integrate a proper React data grid component here */}
          </div>
        )}
      </div>

      <button
        className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        onClick={handleCreateDataset}
      >
        Create Dataset
      </button>
    </div>
  );
};

export default DataEditor;
