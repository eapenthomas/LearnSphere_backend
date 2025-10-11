import React, { useState } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '../../components/DashboardLayout.jsx';
import { useAuth } from '../../contexts/AuthContext.jsx';
import { toast } from 'react-hot-toast';
import { FileText, Upload, Loader, AlertTriangle } from 'lucide-react';

const NotesSummarizer = () => {
  const { user } = useAuth();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');

  const onFileChange = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.type !== 'application/pdf') {
      setError('Please upload a PDF file.');
      setFile(null);
      toast.error('Only PDF files are supported.');
      return;
    }
    setError('');
    setFile(f);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.error('Please select a PDF file first.');
      return;
    }

    try {
      setUploading(true);
      setSummary('');
      setError('');

      const formData = new FormData();
      formData.append('file', file);

      const resp = await fetch('http://localhost:8000/api/notes/summarize', {
        method: 'POST',
        headers: {
          // Backend expects Authorization: Bearer <accessToken>
          Authorization: `Bearer ${user?.accessToken || ''}`
        },
        body: formData
      });

      const result = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        throw new Error(result.detail || 'Failed to summarize notes.');
      }

      if (!result.success) {
        setError(result.message || 'Could not generate a summary.');
        toast.error(result.message || 'Could not generate a summary.');
        return;
      }

      setSummary(result.summary || '');
      toast.success('Summary generated!');
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen student-page-bg">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h1 className="text-heading-xl font-bold mb-2 font-serif" style={{color: '#000000'}}>Notes Summarizer</h1>
            <p className="text-body-lg" style={{color: '#000000'}}>
              Upload your PDF study notes to get a concise, student-friendly summary for quick revision.
            </p>
          </div>

          <div className="student-card-bg rounded-2xl shadow-elegant p-6 border border-border-primary">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex items-center space-x-4">
                <label className="inline-flex items-center px-4 py-2 rounded-xl bg-white border border-gray-200 shadow-sm cursor-pointer hover:bg-gray-50">
                  <Upload className="w-4 h-4 mr-2" />
                  <span className="font-medium">Choose PDF</span>
                  <input type="file" accept="application/pdf" className="hidden" onChange={onFileChange} />
                </label>
                <span className="text-sm" style={{color: '#000000'}}>
                  {file ? file.name : 'No file selected'}
                </span>
              </div>

              {error && (
                <div className="flex items-center space-x-2 text-red-600 bg-red-50 border border-red-200 rounded-xl p-3">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              <div>
                <button
                  type="submit"
                  disabled={uploading}
                  className="btn-primary px-5 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center space-x-2"
                >
                  {uploading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      <span>Summarizing...</span>
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4" />
                      <span>Generate Summary</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {summary && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 student-card-bg rounded-2xl shadow-elegant p-6 border border-border-primary"
            >
              <h2 className="text-heading-md font-semibold mb-3" style={{color: '#000000'}}>Summary</h2>
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap text-sm" style={{color: '#000000'}}>{summary}</pre>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default NotesSummarizer;


