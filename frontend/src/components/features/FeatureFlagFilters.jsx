function FeatureFlagFilters({ environments, selectedEnvironmentId, onEnvironmentChange, searchTerm, onSearchChange, status, onStatusChange }) {
  return (
    <div className="feature-filters">
      <div className="feature-filter-field environment-filter-field">
        <label htmlFor="environment-select">Environment</label>
        <select id="environment-select" value={selectedEnvironmentId} onChange={(event) => onEnvironmentChange(event.target.value)}>
          <option value="all">All environments</option>
          {environments.map((environment) => <option key={environment.id} value={environment.id}>{environment.name}</option>)}
        </select>
      </div>
      <div className="feature-filter-field search-filter-field">
        <label htmlFor="flag-search">Search flags</label>
        <input id="flag-search" type="search" value={searchTerm} onChange={(event) => onSearchChange(event.target.value)} placeholder="Search by name, key, owner..." />
      </div>
      <div className="feature-filter-field status-filter-field">
        <label htmlFor="status-select">Status</label>
        <select id="status-select" value={status} onChange={(event) => onStatusChange(event.target.value)}>
          <option value="all">All</option>
          <option value="enabled">Enabled</option>
          <option value="disabled">Disabled</option>
        </select>
      </div>
    </div>
  );
}

export default FeatureFlagFilters;
