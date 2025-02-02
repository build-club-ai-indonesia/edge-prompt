import React, { useState, useRef } from 'react';
import { MaterialSource, ContentTemplate } from '../../../../backend/src/types';

interface Props {
  onMaterialLoad: (material: MaterialSource) => void;
}

interface Metadata {
  title: string;
  subject: string;
  grade: string;
  chapter: string;
  focusArea: string;
  useSourceLanguage: boolean;
  learningObjectives?: string[];
  templates?: ContentTemplate[];
}

export const MaterialUploader: React.FC<Props> = ({ onMaterialLoad }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const focusAreaRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [metadata, setMetadata] = useState<Metadata>({
    title: '',
    subject: '',
    grade: '',
    chapter: '',
    focusArea: '',
    useSourceLanguage: false,
  });
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const resetForm = () => {
    setFile(null);
    setMetadata({
      title: '',
      subject: '',
      grade: '',
      chapter: '',
      focusArea: '',
      useSourceLanguage: false,
    });
    
    // Reset and focus file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.focus();
    }

    // Focus the focus area input after a short delay to allow for DOM updates
    setTimeout(() => {
      if (focusAreaRef.current) {
        focusAreaRef.current.focus();
      }
    }, 100);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !metadata.focusArea) {
      alert('Please select a file and specify the focus area');
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('metadata', JSON.stringify(metadata));

      const response = await fetch('http://localhost:3001/api/materials/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Create MaterialSource object with the file extension as type
      const fileExt = file.name.split('.').pop()?.toLowerCase() || '';
      onMaterialLoad({
        type: fileExt,
        content: result.content || '',
        metadata: {
          ...metadata,
          learningObjectives: result.objectives || [],
          templates: result.templates || []
        }
      });

      // Clear form using the new resetForm function
      resetForm();
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload material. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="card mb-4">
      <div className="card-header">
        <h5 className="mb-0">
          <i className="bi bi-upload"></i> Upload Teaching Material
        </h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="row">
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  Material File <span className="text-danger">*</span>
                </label>
                <input 
                  ref={fileInputRef}
                  type="file" 
                  className="form-control"
                  accept=".pdf,.docx,.md,.txt"
                  onChange={handleFileChange}
                  required
                />
                <small className="text-muted">
                  Supported formats: PDF, Word, Markdown, Text
                </small>
              </div>
            </div>
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  Focus Area <span className="text-danger">*</span>
                  <small className="text-muted ms-1">(What should students learn from this material?)</small>
                </label>
                <input
                  ref={focusAreaRef}
                  type="text"
                  className="form-control"
                  value={metadata.focusArea}
                  onChange={e => setMetadata({...metadata, focusArea: e.target.value})}
                  placeholder="e.g., Grammar rules, Reading comprehension, etc."
                  required
                />
              </div>
              <div className="mb-3">
                <div className="form-check">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="useSourceLanguage"
                    checked={metadata.useSourceLanguage}
                    onChange={e => setMetadata({...metadata, useSourceLanguage: e.target.checked})}
                  />
                  <label className="form-check-label" htmlFor="useSourceLanguage">
                    Use source material's language for generated content
                    <small className="text-muted d-block">
                      When checked, questions and feedback will be generated in the same language as the teaching material
                    </small>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div className="row">
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  Title <small className="text-muted">(Optional)</small>
                </label>
                <input
                  type="text"
                  className="form-control"
                  value={metadata.title}
                  onChange={e => setMetadata({...metadata, title: e.target.value})}
                  placeholder="Enter material title"
                />
              </div>
            </div>
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  Subject <small className="text-muted">(Optional)</small>
                </label>
                <input
                  type="text"
                  className="form-control"
                  value={metadata.subject}
                  onChange={e => setMetadata({...metadata, subject: e.target.value})}
                  placeholder="e.g., Computer Science"
                />
              </div>
            </div>
          </div>

          <div className="row">
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  Grade Level <small className="text-muted">(Optional)</small>
                </label>
                <input
                  type="text"
                  className="form-control"
                  value={metadata.grade}
                  onChange={e => setMetadata({...metadata, grade: e.target.value})}
                  placeholder="e.g., K-12"
                />
              </div>
            </div>
            <div className="col-md-6">
              <div className="mb-3">
                <label className="form-label">
                  Chapter <small className="text-muted">(Optional)</small>
                </label>
                <input
                  type="text"
                  className="form-control"
                  value={metadata.chapter}
                  onChange={e => setMetadata({...metadata, chapter: e.target.value})}
                  placeholder="e.g., Chapter 1"
                />
              </div>
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isUploading}
          >
            {isUploading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" />
                Processing...
              </>
            ) : (
              <>
                <i className="bi bi-cloud-upload"></i> Upload and Process
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}; 