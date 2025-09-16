import ReactDOM from "react-dom"
import './Modal.css'

function PreviewModal({previewUrl, onClose}) {
    const modalRoot = document.getElementById("modal-root")

    if (!modalRoot || !previewUrl) return null;

    return ReactDOM.createPortal(
        <div className={`modal-overlay preview-modal-overlay ${previewUrl ? "show" : ""}`}>
            <div className="modal-content preview-modal-content">
                <div className='modal-body'>
                    <iframe
                        className='preview-modal__preview' 
                        src={previewUrl} 
                        type="application/pdf" 
                        width='800' 
                        height='1000' 
                    />
                </div>
                <div className="modal-footer">
                    <button
                        className='btn btn-light preview-modal__close' 
                        onClick={onClose}
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
        ,
        modalRoot
    );
}

export default PreviewModal;