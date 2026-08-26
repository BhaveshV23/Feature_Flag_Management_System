function formatUpdatedAt(value) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Not available" : date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function FeatureFlagTable({ flags }) {
  return (
    <div className="feature-table-wrap">
      <table className="feature-table">
        <caption className="visually-hidden">Feature flags for the selected environment</caption>
        <thead><tr><th scope="col">Flag</th><th scope="col">Status</th><th scope="col">Type</th><th scope="col">Owner</th><th scope="col">Default Value</th><th scope="col">Last Updated</th><th scope="col">Actions</th></tr></thead>
        <tbody>
          {flags.map((flag) => (
            <tr key={flag.id}>
              <td><strong>{flag.name || "Unnamed flag"}</strong><span className="flag-key">{flag.key}</span></td>
              <td><span className={`flag-status ${flag.enabled ? "is-enabled" : "is-disabled"}`}>{flag.enabled ? "Enabled" : "Disabled"}</span></td>
              <td>{flag.type || "Not specified"}</td>
              <td>{flag.owner_team || "Unassigned"}</td>
              <td><span className="flag-default-value" title={flag.default_value ?? "Not set"}>{flag.default_value ?? "Not set"}</span></td>
              <td>{formatUpdatedAt(flag.updated_at)}</td>
              <td><button className="table-action" disabled title="Flag details will be available in a future update" type="button">View details</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default FeatureFlagTable;
