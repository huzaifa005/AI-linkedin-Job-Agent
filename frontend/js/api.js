/**
 * API Client — Wraps all fetch() calls to the backend.
 * 
 * Change API_BASE to point to your deployed backend when needed.
 * For local development, it defaults to localhost:8000.
 */

const API_BASE = 'http://localhost:8000/api';

const Api = {
  /**
   * Health check
   * @returns {Promise<{status: string, version: string, app_name: string}>}
   */
  async health() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json();
  },

  /**
   * Upload CV PDF
   * @param {File} file - PDF file
   * @returns {Promise<{cv_id: string, filename: string, text_preview: string, char_count: number}>}
   */
  async uploadCV(file) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/cv/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  /**
   * Start LinkedIn job scraping
   * @param {{role: string, work_type: string, date_posted: string, max_fetch: number}} params
   * @returns {Promise<{session_id: string, status: string}>}
   */
  async startScrape(params) {
    const res = await fetch(`${API_BASE}/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Scrape failed' }));
      throw new Error(err.detail || 'Scrape failed');
    }
    return res.json();
  },

  /**
   * Poll scrape status
   * @param {string} sessionId
   * @returns {Promise<{status: string, jobs_found: number, jobs: Array, logs: Array}>}
   */
  async getScrapeStatus(sessionId) {
    const res = await fetch(`${API_BASE}/scrape/${sessionId}`);
    if (!res.ok) throw new Error(`Status check failed: ${res.status}`);
    return res.json();
  },

  /**
   * Evaluate a single job against CV
   * @param {{cv_id: string, job: object}} params
   * @returns {Promise<{result: object}>}
   */
  async evaluateSingle(params) {
    const res = await fetch(`${API_BASE}/jobs/evaluate-single`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Evaluation failed' }));
      throw new Error(err.detail || 'Evaluation failed');
    }
    return res.json();
  },

  /**
   * Evaluate multiple jobs against CV (batch)
   * @param {{cv_id: string, jobs: Array}} params
   * @returns {Promise<{cv_id: string, total_jobs: number, matched_jobs: number, results: Array}>}
   */
  async evaluateBatch(params) {
    const res = await fetch(`${API_BASE}/jobs/evaluate-batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Batch evaluation failed' }));
      throw new Error(err.detail || 'Batch evaluation failed');
    }
    return res.json();
  },

  /**
   * Generate tailored documents for a matched evaluation
   * @param {{evaluation_id: string}} params
   * @returns {Promise<{doc_id: string, files: Array}>}
   */
  async generateDocuments(params) {
    const res = await fetch(`${API_BASE}/documents/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Document generation failed' }));
      throw new Error(err.detail || 'Document generation failed');
    }
    return res.json();
  },

  /**
   * Get download URL for a document
   * @param {string} docId
   * @param {string} fileType - cv_pdf, cv_docx, cl_pdf, cl_docx
   * @returns {string} Download URL
   */
  getDownloadUrl(docId, fileType) {
    return `${API_BASE}/documents/${docId}/download/${fileType}`;
  },
};

// Make globally available
window.Api = Api;
