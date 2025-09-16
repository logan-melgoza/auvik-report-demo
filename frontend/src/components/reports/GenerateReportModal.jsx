import ReactDOM from "react-dom"
import ModalCard from './ModalCard'
import './Modal.css'

function GenerateReportModal ({isOpen, isGenerating, progress, results, previewUrl, setPreviewUrl, onClose}) {

  const modalRoot = document.getElementById("modal-root")

  if (!modalRoot || !isOpen) return null;

  return ReactDOM.createPortal(
    <div className={`modal-overlay ${isOpen ? "show" : ""}`}>
      <div className='modal-content'>
        {isGenerating ? (
          <>
            <div className='modal-header'>
              <h3>Generating Reports</h3>
            </div>
            <div className='modal-body'>
              <p className='modal-progress'>
                {progress.current + 1} of {progress.total}
              </p>
            </div>
            <div className='modal-footer'>
              <button className='btn btn-secondary'onClick={onClose}>Close</button>
            </div>
          </>
        ) : (
          <>
            <div className='modal-header'>
               <h3>Generated Reports</h3>
            </div>
            <div className='modal-body'>
              {results.map((result) => (
                <ModalCard
                  key={result.domain}
                  domain={result.domain}
                  name={result.name}
                  preview={result.preview}
                  download={result.download}
                  setPreviewUrl={setPreviewUrl} 
                />
              ))}
            </div>
            <div className='modal-footer'>
              <button className='btn btn-secondary'onClick={onClose}>Close</button>
            </div>
          </>
        )}
      </div>
    </div>,
    modalRoot
  );
}

export default GenerateReportModal;