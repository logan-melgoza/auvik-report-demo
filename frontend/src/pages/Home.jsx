import { useState } from 'react'
import TenantList from '../components/tenants/TenantList';
import SelectedTenantList from '../components/tenants/SelectedTenantList';
import GenerateReportButton from '../components/reports/GenerateReportButton';
import GenerateReportModal from '../components/reports/GenerateReportModal';
import PreviewModal from '../components/reports/PreviewModal'
import { generateReport } from '../services/reportService';
import './Home.css';

function Home() {
  const [tenants, setTenants] = useState([]);
  const [selectedTenants, setSelectedTenants] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [results, setResults] = useState([]);
  const [previewUrl, setPreviewUrl] = useState(null)

  async function handleGenerateReports() {
    setIsOpen(true);
    setIsGenerating(true);
    setProgress({ current: 0, total: selectedTenants.length});
    setResults([]);
    
    for (let selectedTenant of selectedTenants) {
      const result = await generateReport(selectedTenant)
      setProgress({ current: progress.current + 1, total: selectedTenants.length});
      setResults(prev => [...prev, result]);
    }
    setIsGenerating(false)
  }

  function toggleTenant(domain) {
    if (selectedTenants.includes(domain)) {
        setSelectedTenants(selectedTenants.filter(d => d !== domain))
    } else {
        setSelectedTenants([...selectedTenants, domain])
    }
  }

  return (
    <div className='home-container'>
      <div className='finder-section'>
        <TenantList 
        tenants={tenants}
        setTenants={setTenants}
        selectedTenants={selectedTenants}
        setSelectedTenants={setSelectedTenants}
        toggleTenant={toggleTenant}
      />
      </div>
      <div className='report-section'>
        <SelectedTenantList 
          tenants={tenants}
          selectedTenants={selectedTenants}
          setSelectedTenants={setSelectedTenants}
          toggleTenant={toggleTenant}
        />
        <GenerateReportButton 
          selectedTenants={selectedTenants}
          handleGenerateReports={handleGenerateReports}
        />
      </div>
      { isOpen && <GenerateReportModal 
        isOpen={isOpen}
        isGenerating={isGenerating}
        progress={progress}
        results={results}
        previewUrl={previewUrl}
        setPreviewUrl={setPreviewUrl}
        onClose={() => setIsOpen(false)}
      />}
      {previewUrl && (
        <PreviewModal 
          previewUrl={previewUrl}
          onClose={() => setPreviewUrl(null)}
        />
      )}
    </div>
  );
}

export default Home;