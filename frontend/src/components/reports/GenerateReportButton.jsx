import { useAuth } from '../../context/AuthContext'
import './GenerateReportButton.css'

function GenerateReportButton({selectedTenants, handleGenerateReports}) {
  const { user } = useAuth()
  
  return (
    <button
      className='btn btn-primary generate-report'
      onClick={handleGenerateReports}
      disabled={selectedTenants.length === 0 || !user}
    >
      Generate Report(s)
    </button>
  );
}

export default GenerateReportButton;
