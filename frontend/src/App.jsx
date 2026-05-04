import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, FileText, Check, X, Terminal, RefreshCw, Cpu } from 'lucide-react';
import ReactDiffViewer from 'react-diff-viewer-continued';

const App = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeResult, setActiveResult] = useState(null);

  const fetchResults = async () => {
    try {
      const response = await axios.get('http://localhost:8000/results');
      setResults(response.data);
    } catch (error) {
      console.error("Error fetching results", error);
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchResults, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (filePath, approved) => {
    try {
      await axios.post('http://localhost:8000/approve', {
        file_path: filePath,
        approved: approved
      });
      fetchResults();
    } catch (error) {
      console.error("Error approving patch", error);
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-7xl mx-auto">
      <header className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-4xl font-bold font-['Outfit'] mb-2 flex items-center gap-3">
            <Shield className="w-10 h-10 text-purple-500" />
            <span className="gradient-text">Self-Healing Docs</span>
          </h1>
          <p className="text-gray-400">Autonomous Code-to-Doc Synchronization</p>
        </div>
        <div className="flex gap-4">
          <div className="glass-card px-4 py-2 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-mono uppercase tracking-widest text-blue-400">System Live</span>
          </div>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Analysis Log */}
        <div className="lg:col-span-1 glass-card p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-purple-400" />
            Analysis Log
          </h2>
          <div className="space-y-4 max-h-[600px] overflow-y-auto">
            {results.length === 0 && (
              <div className="text-gray-500 italic text-sm p-4 text-center border border-dashed border-gray-800 rounded-lg">
                No changes detected yet. Modify a .py or .js file to begin.
              </div>
            )}
            {results.map((res, idx) => (
              <div 
                key={idx} 
                className={`p-4 rounded-xl cursor-pointer transition-all ${activeResult === idx ? 'bg-purple-500/20 border-purple-500/50 border' : 'bg-white/5 border border-transparent'}`}
                onClick={() => setActiveResult(idx)}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-mono text-gray-500 truncate max-w-[150px]">
                    {res.file_path.split('/').pop()}
                  </span>
                  <span className="text-[10px] bg-purple-500/30 px-2 py-0.5 rounded uppercase font-bold text-purple-300">
                    {res.status}
                  </span>
                </div>
                <p className="text-sm line-clamp-2">{res.code_intent}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Diff & Approval */}
        <div className="lg:col-span-2 glass-card p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            Proposed Documentation Patch
          </h2>
          {activeResult !== null ? (
            <div className="space-y-6">
              <div className="rounded-lg overflow-hidden border border-gray-800">
                <ReactDiffViewer 
                  oldValue={results[activeResult].retrieved_docs.join('\n')} 
                  newValue={results[activeResult].generated_patch} 
                  splitView={true} 
                  useDarkTheme={true}
                  styles={{
                    variables: {
                      dark: {
                        diffViewerBackground: '#0e0e11',
                        addedBackground: '#064e3b',
                        addedColor: '#34d399',
                        removedBackground: '#7f1d1d',
                        removedColor: '#f87171',
                      }
                    }
                  }}
                />
              </div>
              <div className="flex gap-4">
                <button 
                  onClick={() => handleApprove(results[activeResult].file_path, true)}
                  className="primary-btn flex-1 flex items-center justify-center gap-2"
                >
                  <Check className="w-5 h-5" />
                  Approve and Update Doc
                </button>
                <button 
                  onClick={() => handleApprove(results[activeResult].file_path, false)}
                  className="secondary-btn flex-1 flex items-center justify-center gap-2"
                >
                  <X className="w-5 h-5" />
                  Reject Change
                </button>
              </div>
            </div>
          ) : (
            <div className="h-[400px] flex flex-col items-center justify-center text-gray-500">
              <RefreshCw className="w-12 h-12 mb-4 opacity-20 animate-spin-slow" />
              <p>Select an item from the log to review the patch.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
