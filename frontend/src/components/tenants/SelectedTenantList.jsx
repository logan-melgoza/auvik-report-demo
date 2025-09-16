import { CSSTransition, TransitionGroup } from 'react-transition-group'; 
import TenantCard from './TenantCard';
import './TenantList.css'

function SelectedTenantList ({tenants, selectedTenants, toggleTenant}) {
  const selectedTenantsObjects = tenants.filter(tenant => selectedTenants.includes(tenant.domain))

  return (
    <div className='tenant-list-container'>
      <h2>Selected Tenants</h2>
      { selectedTenants.length == 0 ? (
        <p>No Tenants Currently Selected</p>
      ) : (
        <div className='tenant-grid'>
          {selectedTenantsObjects.map((tenant) => (
            <TenantCard 
              key={tenant.domain}
              domain={tenant.domain}
              name={tenant.name}
              onClick={() => toggleTenant(tenant.domain)}
            />
          ))}
        </div> 
      )}
    </div>
  );
}

export default SelectedTenantList;