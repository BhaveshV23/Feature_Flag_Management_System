function formatDate(value) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Not available" : date.toLocaleDateString(undefined, { dateStyle: "medium" });
}

function EnvironmentTable({ environments, onEdit, onDelete }) {
  return <div className="environment-table-wrap"><table className="environment-table"><caption className="visually-hidden">Configured environments</caption><thead><tr><th>Name</th><th>Description</th><th>Status</th><th>Created</th><th>Updated</th><th><span className="visually-hidden">Actions</span></th></tr></thead><tbody>{environments.map((environment) => <tr key={environment.id}><td><strong>{environment.name}</strong><small>ID {environment.id}</small></td><td data-label="Description">{environment.description || "No description"}</td><td data-label="Status"><span className={`environment-status ${environment.is_active ? "is-active" : "is-inactive"}`}>{environment.is_active ? "Active" : "Inactive"}</span></td><td data-label="Created">{formatDate(environment.created_at)}</td><td data-label="Updated">{formatDate(environment.updated_at)}</td><td data-label="Actions"><div className="environment-actions"><button className="text-action" onClick={() => onEdit(environment)} type="button">Edit</button><button className="text-action destructive" onClick={() => onDelete(environment)} type="button">Delete</button></div></td></tr>)}</tbody></table></div>;
}

export default EnvironmentTable;
