import { ZoomIn, ZoomOut, Maximize, Download, X } from "lucide-react";

interface PdfViewerProps {
  pdfUrl: string | null;
  pageNumber: number | null;
  onClose?: () => void;
}

export function PdfViewer({ pdfUrl, pageNumber, onClose }: PdfViewerProps) {
  if (!pdfUrl) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-container-low/30 p-8">
        <div className="text-center text-secondary">
          <p className="font-headline-sm text-headline-sm">No Document Selected</p>
          <p className="font-body-md mt-2">Click any statutory citation chip to inspect the original source document.</p>
        </div>
      </div>
    );
  }

  const filename = pdfUrl.split('/').pop()?.replace('.pdf', '') || 'Document';
  
  return (
    <div className="flex flex-col h-full w-full">
      {/* Viewer Toolbar */}
      <div className="h-14 border-b border-outline-variant/30 bg-surface/70 backdrop-blur-md flex items-center justify-between px-4 shrink-0 shadow-sm">
        <div className="flex items-center gap-4">
          <h3 className="font-ui-label-bold text-ui-label-bold text-on-surface truncate max-w-[250px]">{filename}</h3>
          {pageNumber && (
            <>
              <div className="h-4 w-px bg-outline-variant/50"></div>
              <span className="font-mono-label text-mono-label text-secondary bg-surface-container-low/50 px-2 py-1 rounded-md border border-outline-variant/40">
                Page {pageNumber}
              </span>
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button className="text-secondary hover:text-primary-container transition-colors p-1.5 hover:bg-surface-container-low/50 rounded-md border border-transparent hover:border-outline-variant/40 flex items-center">
            <ZoomOut className="w-4 h-4 font-light" />
          </button>
          <button className="text-secondary hover:text-primary-container transition-colors p-1.5 hover:bg-surface-container-low/50 rounded-md border border-transparent hover:border-outline-variant/40 flex items-center">
            <ZoomIn className="w-4 h-4 font-light" />
          </button>
          <div className="h-4 w-px bg-outline-variant/50 mx-1"></div>
          <button className="text-secondary hover:text-primary-container transition-colors p-1.5 hover:bg-surface-container-low/50 rounded-md border border-transparent hover:border-outline-variant/40 flex items-center" title="Full Screen">
            <Maximize className="w-4 h-4 font-light" />
          </button>
          <button className="text-secondary hover:text-primary-container transition-colors p-1.5 hover:bg-surface-container-low/50 rounded-md border border-transparent hover:border-outline-variant/40 flex items-center" title="Download">
            <Download className="w-4 h-4 font-light" />
          </button>
          {onClose && (
            <>
              <div className="h-4 w-px bg-outline-variant/50 mx-1"></div>
              <button 
                onClick={onClose} 
                className="text-secondary hover:text-red-500 transition-colors p-1.5 hover:bg-red-500/10 rounded-md border border-transparent hover:border-red-500/30 flex items-center" 
                title="Close Viewer"
              >
                <X className="w-4 h-4 font-light" />
              </button>
            </>
          )}
        </div>
      </div>
      
      {/* Document Canvas - Embedded PDF */}
      <div className="flex-1 overflow-hidden bg-surface-container-low/30 relative">
        <iframe 
          src={`${pdfUrl}${pageNumber ? `#page=${pageNumber}` : ''}`} 
          className="w-full h-full border-0"
          title="PDF Document Viewer"
        />
      </div>
    </div>
  );
}
