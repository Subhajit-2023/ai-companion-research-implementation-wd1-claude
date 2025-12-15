import { useState, useEffect } from 'react';
import {
  BookOpen,
  Upload,
  Search,
  Trash2,
  FileText,
  File,
  Loader2,
  FolderOpen,
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { documentApi } from '../services/api';
import useStore from '../store/useStore';

const fileTypeIcons = {
  pdf: { icon: FileText, color: 'text-red-400' },
  epub: { icon: BookOpen, color: 'text-emerald-400' },
  txt: { icon: File, color: 'text-surface-400' },
  md: { icon: File, color: 'text-primary-400' },
  py: { icon: File, color: 'text-amber-400' },
  js: { icon: File, color: 'text-yellow-400' },
};

function DocumentCard({ doc, onDelete }) {
  const typeConfig = fileTypeIcons[doc.file_type] || fileTypeIcons.txt;
  const Icon = typeConfig.icon;

  return (
    <div className="card hover:border-primary-500/50 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="p-3 bg-surface-700 rounded-lg">
            <Icon className={`w-6 h-6 ${typeConfig.color}`} />
          </div>
          <div>
            <h3 className="text-white font-medium">{doc.title}</h3>
            <p className="text-sm text-surface-400">{doc.author}</p>
            <div className="flex items-center gap-4 mt-2">
              <span className="text-xs text-surface-500">
                {doc.total_pages} pages
              </span>
              <span className="text-xs text-surface-500">
                {doc.total_chunks} chunks
              </span>
              <span className="badge badge-info uppercase">{doc.file_type}</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => onDelete(doc.id)}
          className="p-2 text-surface-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

function Knowledge() {
  const { documents, loading, fetchDocuments, addDocument, deleteDocument } = useStore();
  const [filePath, setFilePath] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!filePath.trim()) return;

    setAdding(true);
    const success = await addDocument(filePath);
    setAdding(false);
    if (success) {
      setFilePath('');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const response = await documentApi.search(searchQuery, 10);
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setSearching(false);
    }
  };

  const handleDelete = async (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      await deleteDocument(docId);
    }
  };

  const stats = {
    totalDocs: documents.length,
    totalChunks: documents.reduce((acc, doc) => acc + (doc.total_chunks || 0), 0),
    byType: documents.reduce((acc, doc) => {
      acc[doc.file_type] = (acc[doc.file_type] || 0) + 1;
      return acc;
    }, {}),
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Knowledge Base</h1>
        <p className="text-surface-400 mt-1">
          Manage your documents and search the knowledge base
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="stat-card">
          <p className="stat-label">Total Documents</p>
          <p className="stat-value">{stats.totalDocs}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Total Chunks</p>
          <p className="stat-value">{stats.totalChunks.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">PDFs</p>
          <p className="stat-value text-red-400">{stats.byType.pdf || 0}</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">EPUBs</p>
          <p className="stat-value text-emerald-400">{stats.byType.epub || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="card-header flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Add Document
          </h3>
          <form onSubmit={handleAdd} className="space-y-4">
            <div>
              <label className="block text-sm text-surface-400 mb-2">File Path</label>
              <input
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="/path/to/your/document.pdf"
                className="input"
              />
              <p className="text-xs text-surface-500 mt-2">
                Supported formats: PDF, EPUB, TXT, MD, Python, JavaScript
              </p>
            </div>
            <button
              type="submit"
              disabled={adding || !filePath.trim()}
              className="btn btn-primary w-full flex items-center justify-center gap-2"
            >
              {adding ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Add to Knowledge Base
                </>
              )}
            </button>
          </form>
        </div>

        <div className="card">
          <h3 className="card-header flex items-center gap-2">
            <Search className="w-5 h-5" />
            Search Knowledge
          </h3>
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search your documents..."
                className="input pl-12"
              />
            </div>
            <button
              type="submit"
              disabled={searching || !searchQuery.trim()}
              className="btn btn-primary w-full flex items-center justify-center gap-2"
            >
              {searching ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Search
                </>
              )}
            </button>
          </form>

          {searchResults && (
            <div className="mt-4 pt-4 border-t border-surface-700">
              <h4 className="text-sm font-medium text-surface-300 mb-3">
                Results ({searchResults.total})
              </h4>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {searchResults.results.map((result, index) => (
                  <div
                    key={index}
                    className="p-3 bg-surface-700/50 rounded-lg border border-surface-600"
                  >
                    <p className="text-sm text-primary-400 mb-1">
                      {result.metadata?.document_title || 'Unknown Document'}
                    </p>
                    <p className="text-sm text-surface-300 line-clamp-3">
                      {result.content}
                    </p>
                    {result.distance !== undefined && (
                      <p className="text-xs text-surface-500 mt-2">
                        Relevance: {((1 - result.distance) * 100).toFixed(0)}%
                      </p>
                    )}
                  </div>
                ))}
                {searchResults.results.length === 0 && (
                  <p className="text-center text-surface-500 py-4">No results found</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-white mb-4">Documents</h3>
        {loading.documents ? (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-500 mx-auto" />
            <p className="text-surface-400 mt-2">Loading documents...</p>
          </div>
        ) : documents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <DocumentCard key={doc.id} doc={doc} onDelete={handleDelete} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FolderOpen className="w-12 h-12 mx-auto text-surface-600 mb-4" />
            <p className="text-surface-400">No documents yet</p>
            <p className="text-sm text-surface-500 mt-1">
              Add PDFs, EPUBs, or text files to build your knowledge base
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Knowledge;
