import { useEffect, useMemo, useState } from "react";
import { createFlag, getEnvironments, getFlags } from "../services/api";
import FeatureFlagForm from "../components/features/FeatureFlagForm";
import FeatureFlagFilters from "../components/features/FeatureFlagFilters";
import FeatureFlagSummary from "../components/features/FeatureFlagSummary";
import FeatureFlagTable from "../components/features/FeatureFlagTable";

function FeaturesPage() {
  const [flags, setFlags] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [selectedEnvironmentId, setSelectedEnvironmentId] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [status, setStatus] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadData = async () => {
    setIsLoading(true);
    setError("");
    try {
      const [flagResult, environmentResult] = await Promise.all([getFlags(), getEnvironments()]);
      const nextEnvironments = Array.isArray(environmentResult) ? environmentResult : [];
      setFlags(Array.isArray(flagResult) ? flagResult : []);
      setEnvironments(nextEnvironments);
      setSelectedEnvironmentId((currentId) => currentId || String(nextEnvironments[0]?.id || ""));
    } catch (requestError) {
      setError(requestError.message || "Unable to load feature flags.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [flagResult, environmentResult] = await Promise.all([getFlags(), getEnvironments()]);
        const nextEnvironments = Array.isArray(environmentResult) ? environmentResult : [];
        setFlags(Array.isArray(flagResult) ? flagResult : []);
        setEnvironments(nextEnvironments);
        setSelectedEnvironmentId((currentId) => currentId || String(nextEnvironments[0]?.id || ""));
      } catch (requestError) {
        setError(requestError.message || "Unable to load feature flags.");
      } finally {
        setIsLoading(false);
      }
    }

    loadInitialData();
  }, []);

  const selectedEnvironment = environments.find((environment) => String(environment.id) === String(selectedEnvironmentId));
  const environmentFlags = useMemo(() => flags.filter((flag) => String(flag.environment_id) === String(selectedEnvironmentId)), [flags, selectedEnvironmentId]);
  const filteredFlags = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();
    return environmentFlags.filter((flag) => {
      const matchesStatus = status === "all" || (status === "enabled" ? flag.enabled : !flag.enabled);
      const searchableText = [flag.name, flag.key, flag.description, flag.owner_team].filter(Boolean).join(" ").toLowerCase();
      return matchesStatus && (!query || searchableText.includes(query));
    });
  }, [environmentFlags, searchTerm, status]);

  const handleCreateFlag = async (flagData) => {
    setIsCreating(true);
    setCreateError("");
    try {
      await createFlag(flagData);
      await loadData();
      setIsFormOpen(false);
      setSuccessMessage(`Flag created in ${selectedEnvironment?.name || "the selected environment"}.`);
    } catch (requestError) {
      setCreateError(requestError.message || "The flag could not be created.");
    } finally {
      setIsCreating(false);
    }
  };

  if (isLoading) {
    return <section className="feature-page-state" role="status"><div className="dashboard-state-mark" aria-hidden="true">◌</div><h2>Loading feature flags</h2><p>Fetching flags and environments from the workspace.</p></section>;
  }

  if (error) {
    return <section className="feature-page-state feature-page-error" role="alert"><div className="dashboard-state-mark" aria-hidden="true">!</div><h2>Feature flags could not be loaded</h2><p>There was a problem connecting to the feature management service.</p><button className="btn secondary" onClick={loadData} type="button">Retry</button></section>;
  }

  if (environments.length === 0) {
    return <section className="feature-page-state"><div className="dashboard-state-mark" aria-hidden="true">◈</div><h2>No environments available</h2><p>Create an environment before managing its feature flags.</p></section>;
  }

  const enabledCount = filteredFlags.filter((flag) => flag.enabled).length;
  const disabledCount = filteredFlags.length - enabledCount;

  return (
    <section className="features-page">
      {successMessage && <div className="feature-success-message" role="status">{successMessage}<button aria-label="Dismiss success message" onClick={() => setSuccessMessage("")} type="button">×</button></div>}
      <div className="feature-page-header">
        <div><p className="dashboard-eyebrow">Release configuration</p><h2>Feature Flags</h2><p>Review flag state and release configuration across each environment.</p></div>
        <button className="btn primary create-flag-button" onClick={() => { setCreateError(""); setIsFormOpen(true); }} type="button">+ Create Flag</button>
      </div>
      <FeatureFlagFilters environments={environments} selectedEnvironmentId={selectedEnvironmentId} onEnvironmentChange={setSelectedEnvironmentId} searchTerm={searchTerm} onSearchChange={setSearchTerm} status={status} onStatusChange={setStatus} />
      <div className="selected-environment-note">Viewing <strong>{selectedEnvironment?.name || "selected environment"}</strong> · Summary reflects current search and status filters.</div>
      <FeatureFlagSummary total={filteredFlags.length} enabled={enabledCount} disabled={disabledCount} />
      {environmentFlags.length === 0 ? (
        <div className="feature-empty-state"><h3>No flags in this environment</h3><p>{selectedEnvironment?.name || "This environment"} does not have any feature flags yet.</p></div>
      ) : filteredFlags.length === 0 ? (
        <div className="feature-empty-state"><h3>No matching flags</h3><p>Try a different search term or status filter.</p></div>
      ) : <FeatureFlagTable flags={filteredFlags} />}
      {isFormOpen && <FeatureFlagForm environments={environments} selectedEnvironmentId={selectedEnvironmentId} isSubmitting={isCreating} onClose={() => !isCreating && setIsFormOpen(false)} onSubmit={handleCreateFlag} submitError={createError} />}
    </section>
  );
}

export default FeaturesPage;
