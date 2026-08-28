import { useEffect, useMemo, useState } from "react";
import { createEnvironment, deleteEnvironment, getEnvironments, updateEnvironment } from "../services/api";
import DeleteEnvironmentDialog from "../components/environments/DeleteEnvironmentDialog";
import EnvironmentForm from "../components/environments/EnvironmentForm";
import EnvironmentTable from "../components/environments/EnvironmentTable";

function EnvironmentsPage() {
  const [environments, setEnvironments] = useState([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [formEnvironment, setFormEnvironment] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const [success, setSuccess] = useState("");

  const loadEnvironments = async () => {
    setIsLoading(true);
    setError("");
    try {
      const result = await getEnvironments();
      setEnvironments(Array.isArray(result) ? result : []);
    } catch (requestError) {
      setError(requestError.message || "Unable to load environments.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const load = async () => { await loadEnvironments(); };
    load();
  }, []);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return environments.filter((environment) => !query || `${environment.name} ${environment.description || ""}`.toLowerCase().includes(query));
  }, [environments, search]);

  const save = async (payload) => {
    setIsSaving(true);
    setFormError("");
    try {
      if (formEnvironment) await updateEnvironment(formEnvironment.id, payload);
      else await createEnvironment(payload);
      await loadEnvironments();
      setIsFormOpen(false);
      setSuccess(`Environment ${formEnvironment ? "updated" : "created"}.`);
    } catch (requestError) {
      setFormError(requestError.message || "The environment could not be saved.");
    } finally {
      setIsSaving(false);
    }
  };

  const confirmDelete = async () => {
    setIsDeleting(true);
    setDeleteError("");
    try {
      await deleteEnvironment(deleteTarget.id);
      await loadEnvironments();
      setDeleteTarget(null);
      setSuccess("Environment deleted.");
    } catch (requestError) {
      setDeleteError(requestError.message || "The environment could not be deleted.");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <section className="environment-page">
      <div className="feature-page-header">
        <div><p className="dashboard-eyebrow">Workspace configuration</p><h2>Environments</h2><p>Organize feature releases into clear, independently managed contexts.</p></div>
        <button className="btn primary" onClick={() => { setFormEnvironment(null); setFormError(""); setIsFormOpen(true); }} type="button">+ New Environment</button>
      </div>
      {success && <div className="feature-success-message" role="status">{success}<button className="notification-close" aria-label="Dismiss notification" title="Dismiss" onClick={() => setSuccess("")} type="button">×</button></div>}
      <div className="environment-toolbar"><label htmlFor="environment-search">Search environments</label><input id="environment-search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by name or description" /></div>
      {isLoading ? <div className="feature-page-state" role="status"><div className="dashboard-state-mark" aria-hidden="true">◌</div><h2>Loading environments</h2><p>Fetching configured release contexts.</p></div> : error ? <div className="feature-page-state feature-page-error" role="alert"><div className="dashboard-state-mark" aria-hidden="true">!</div><h2>Environments could not be loaded</h2><p>{error}</p><button className="btn secondary" onClick={loadEnvironments} type="button">Retry</button></div> : environments.length === 0 ? <div className="feature-empty-state"><h3>No environments yet</h3><p>Create your first environment to organize feature releases.</p><button className="btn primary" onClick={() => { setFormEnvironment(null); setIsFormOpen(true); }} type="button">Create Environment</button></div> : filtered.length === 0 ? <div className="feature-empty-state"><h3>No matching environments</h3><p>Try a different name or description.</p></div> : <EnvironmentTable environments={filtered} onEdit={(environment) => { setFormEnvironment(environment); setFormError(""); setIsFormOpen(true); }} onDelete={(environment) => { setDeleteTarget(environment); setDeleteError(""); }} />}
      {isFormOpen && <EnvironmentForm environment={formEnvironment} isSubmitting={isSaving} submitError={formError} onClose={() => !isSaving && setIsFormOpen(false)} onSubmit={save} />}
      {deleteTarget && <DeleteEnvironmentDialog environment={deleteTarget} isDeleting={isDeleting} error={deleteError} onClose={() => !isDeleting && setDeleteTarget(null)} onConfirm={confirmDelete} />}
    </section>
  );
}

export default EnvironmentsPage;
