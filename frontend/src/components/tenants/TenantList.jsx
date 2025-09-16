import { useState, useEffect } from "react";
import { getTenants } from "../../services/tenantService";
import TenantCard from "./TenantCard";
import './TenantList.css'

function TenantList({tenants, setTenants, selectedTenants, setSelectedTenants, toggleTenant}) {

  useEffect(() => {
    getTenants().then(setTenants).catch(console.error());
  }, []);

  return (
    <div className="tenant-list-container">
      <h2>Tenants</h2>
      <div className="tenant-grid">
        {tenants.map((tenant) => (
          <TenantCard
            key={tenant.domain}
            domain={tenant.domain}
            name={tenant.name}
            selected={selectedTenants.includes(tenant.domain)}
            onClick={() => toggleTenant(tenant.domain)}
          />
        ))}
      </div>
    </div>
  );
}

export default TenantList;
