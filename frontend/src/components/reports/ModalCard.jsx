import './ModalCard.css'

function ModalCard({domain, name, preview, download, setPreviewUrl}) {

  async function handleDownload(url, filename) {
    const res = await fetch(`${url}`);
    const blob = await res.blob();
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    link.remove();
  }

  return (
    <div className='card modal-card'>
      <div className='card-body modal-card-body'>
        <h5 className='modal-body__domain'>
          {name}
        </h5>
        <div className='modal-body__buttons'>
          <button 
            className='btn btn-primary btn-sm modal-card-button'
            onClick={() => setPreviewUrl(`${preview}`)}
          >
            Preview
          </button>
          <button 
            className='btn btn-primary btn-sm modal-card-button'
            onClick={() => handleDownload(download, `${domain}-report.pdf`)}
          >
            Download
          </button>
        </div>
      </div>
    </div>
  );
}

export default ModalCard;