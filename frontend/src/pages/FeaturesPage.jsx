import { useEffect, useMemo, useState } from "react";
import { createFlag, createTargetingRule, deleteFlag, deleteTargetingRule, getEnvironments, getFlag, getFlags, getTargetingRules, updateFlag, updateTargetingRule } from "../services/api";
import FeatureFlagDetailsModal from "../components/features/FeatureFlagDetailsModal";
import FeatureFlagEditForm from "../components/features/FeatureFlagEditForm";
import FeatureFlagForm from "../components/features/FeatureFlagForm";
import FeatureFlagFilters from "../components/features/FeatureFlagFilters";
import FeatureFlagSummary from "../components/features/FeatureFlagSummary";
import FeatureFlagTable from "../components/features/FeatureFlagTable";
import TargetingRuleForm from "../components/features/TargetingRuleForm";

const ALL_ENVIRONMENTS = "all";
import DeleteFlagDialog from "../components/features/DeleteFlagDialog";

function FeaturesPage() {
  const [flags, setFlags] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [selectedEnvironmentId, setSelectedEnvironmentId] = useState(ALL_ENVIRONMENTS);
  const [searchTerm, setSearchTerm] = useState("");
  const [status, setStatus] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  const [detailsFlag, setDetailsFlag] = useState(null);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState("");
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateError, setUpdateError] = useState("");
  const [selectedFlagId, setSelectedFlagId] = useState(null);
  const [targetingRules, setTargetingRules] = useState([]);
  const [isRulesLoading, setIsRulesLoading] = useState(false);
  const [rulesError, setRulesError] = useState("");
  const [isRuleFormOpen, setIsRuleFormOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [isRuleSaving, setIsRuleSaving] = useState(false);
  const [ruleSubmitError, setRuleSubmitError] = useState("");
  const [isRuleDeleting, setIsRuleDeleting] = useState(false);
  const [ruleActionError, setRuleActionError] = useState("");
  const [deletingFlag, setDeletingFlag] = useState(null);
  const [isFlagDeleting, setIsFlagDeleting] = useState(false);
  const [flagDeleteError, setFlagDeleteError] = useState("");

  const loadData = async () => {
    setIsLoading(true);
    setError("");
    try {
      const [flagResult, environmentResult] = await Promise.all([getFlags(), getEnvironments()]);
      const nextEnvironments = Array.isArray(environmentResult) ? environmentResult : [];
      setFlags(Array.isArray(flagResult) ? flagResult : []);
      setEnvironments(nextEnvironments);
      setSelectedEnvironmentId((currentId) => currentId || ALL_ENVIRONMENTS);
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
        setSelectedEnvironmentId((currentId) => currentId || ALL_ENVIRONMENTS);
      } catch (requestError) {
        setError(requestError.message || "Unable to load feature flags.");
      } finally {
        setIsLoading(false);
      }
    }

    loadInitialData();
  }, []);

  const selectedEnvironment = environments.find((environment) => String(environment.id) === String(selectedEnvironmentId));
  const environmentFlags = useMemo(() => selectedEnvironmentId === ALL_ENVIRONMENTS ? flags : flags.filter((flag) => String(flag.environment_id) === String(selectedEnvironmentId)), [flags, selectedEnvironmentId]);
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

  const loadFlagDetails = async (flagId) => {
    setIsDetailsLoading(true);
    setDetailsError("");
    try {
      const flag = await getFlag(flagId);
      if (!flag) throw new Error("This flag no longer exists.");
      setDetailsFlag(flag);
    } catch (requestError) {
      setDetailsError(requestError.message || "Unable to load flag details.");
    } finally {
      setIsDetailsLoading(false);
    }
  };

  const openDetails = (flagId) => {
    setSelectedFlagId(flagId);
    setDetailsFlag(null);
    setUpdateError("");
    setIsDetailsOpen(true);
    loadFlagDetails(flagId);
    loadTargetingRules();
  };

  const loadTargetingRules = async () => {
    setIsRulesLoading(true);
    setRulesError("");
    try {
      const result = await getTargetingRules();
      setTargetingRules(Array.isArray(result) ? result : []);
    } catch (requestError) {
      setRulesError(requestError.message || "Unable to load targeting rules.");
    } finally {
      setIsRulesLoading(false);
    }
  };

  const closeDetails = () => {
    if (isUpdating) return;
    setIsDetailsOpen(false);
    setDetailsFlag(null);
    setDetailsError("");
    setSelectedFlagId(null);
    setTargetingRules([]);
    setRulesError("");
  };

  const refreshUpdatedFlag = async (flagId) => {
    const [flag, flagResult] = await Promise.all([getFlag(flagId), getFlags()]);
    if (!flag) throw new Error("The flag could not be found after saving.");
    setDetailsFlag(flag);
    setFlags(Array.isArray(flagResult) ? flagResult : []);
    return flag;
  };

  const handleUpdateFlag = async (payload, successText, closeEdit = true) => {
    if (!detailsFlag || isUpdating) return;
    setIsUpdating(true);
    setUpdateError("");
    try {
      await updateFlag(detailsFlag.id, payload);
      await refreshUpdatedFlag(detailsFlag.id);
      if (closeEdit) {
        setIsEditOpen(false);
        setIsDetailsOpen(true);
      }
      setSuccessMessage(successText);
    } catch (requestError) {
      setUpdateError(requestError.message || "The flag could not be updated.");
    } finally {
      setIsUpdating(false);
    }
  };

  const buildUpdatePayload = (flag, enabled = flag.enabled) => ({ key: flag.key, type: flag.type, default_value: flag.default_value ?? "", enabled, description: flag.description ?? "", owner_team: flag.owner_team ?? "" });
  const selectedFlagRules = useMemo(() => targetingRules.filter((rule) => String(rule.flag_id) === String(detailsFlag?.id)).sort((a, b) => a.priority - b.priority), [targetingRules, detailsFlag]);

  const openRuleForm = (rule = null) => {
    setEditingRule(rule);
    setRuleSubmitError("");
    setRuleActionError("");
    setIsDetailsOpen(false);
    setIsRuleFormOpen(true);
  };

  const closeRuleForm = () => {
    if (isRuleSaving) return;
    setIsRuleFormOpen(false);
    setEditingRule(null);
    setRuleSubmitError("");
    setIsDetailsOpen(true);
  };

  const handleSaveRule = async (payload) => {
    if (isRuleSaving) return;
    setIsRuleSaving(true);
    setRuleSubmitError("");
    try {
      if (editingRule) await updateTargetingRule(editingRule.id, payload);
      else await createTargetingRule(payload);
      await loadTargetingRules();
      setIsRuleFormOpen(false);
      setEditingRule(null);
      setIsDetailsOpen(true);
      setSuccessMessage(`Targeting rule ${editingRule ? "updated" : "added"}.`);
    } catch (requestError) {
      setRuleSubmitError(requestError.message || "The targeting rule could not be saved.");
    } finally {
      setIsRuleSaving(false);
    }
  };

  const handleDeleteRule = async (ruleId) => {
    if (isRuleDeleting) return;
    setIsRuleDeleting(true);
    setRuleActionError("");
    try {
      await deleteTargetingRule(ruleId);
      await loadTargetingRules();
      setSuccessMessage("Targeting rule deleted.");
    } catch (requestError) {
      setRuleActionError(requestError.message || "The targeting rule could not be deleted.");
    } finally {
      setIsRuleDeleting(false);
    }
  };

  const handleDeleteFlag = async () => {
    if (!deletingFlag || isFlagDeleting) return;
    setIsFlagDeleting(true);
    setFlagDeleteError("");
    try {
      await deleteFlag(deletingFlag.id);
      setFlags((currentFlags) => currentFlags.filter((flag) => flag.id !== deletingFlag.id));
      setDeletingFlag(null);
      setIsDetailsOpen(false);
      setDetailsFlag(null);
      setSelectedFlagId(null);
      setSuccessMessage("Flag deleted successfully.");
    } catch (requestError) {
      setFlagDeleteError(requestError.message || "The flag could not be deleted.");
    } finally {
      setIsFlagDeleting(false);
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
      <div className="selected-environment-note">Viewing <strong>{selectedEnvironment?.name || "All environments"}</strong> · Summary reflects current search and status filters.</div>
      <FeatureFlagSummary total={filteredFlags.length} enabled={enabledCount} disabled={disabledCount} />
      {environmentFlags.length === 0 ? (
        <div className="feature-empty-state"><h3>No flags in this environment</h3><p>{selectedEnvironment?.name || "This environment"} does not have any feature flags yet.</p></div>
      ) : filteredFlags.length === 0 ? (
        <div className="feature-empty-state"><h3>No matching flags</h3><p>Try a different search term or status filter.</p></div>
      ) : <FeatureFlagTable flags={filteredFlags} environments={environments} onViewDetails={openDetails} />}
      {isFormOpen && <FeatureFlagForm environments={environments} selectedEnvironmentId={selectedEnvironmentId === ALL_ENVIRONMENTS ? "" : selectedEnvironmentId} isSubmitting={isCreating} onClose={() => !isCreating && setIsFormOpen(false)} onSubmit={handleCreateFlag} submitError={createError} />}
      {isDetailsOpen && <FeatureFlagDetailsModal flag={detailsFlag} environmentName={environments.find((environment) => environment.id === detailsFlag?.environment_id)?.name} isLoading={isDetailsLoading} error={detailsError} actionError={updateError} isSaving={isUpdating} targetingRules={selectedFlagRules} isRulesLoading={isRulesLoading} rulesError={rulesError} ruleActionError={ruleActionError} isDeletingRule={isRuleDeleting} onClose={closeDetails} onRetry={() => selectedFlagId && loadFlagDetails(selectedFlagId)} onRetryRules={loadTargetingRules} onEdit={() => { setUpdateError(""); setIsEditOpen(true); setIsDetailsOpen(false); }} onToggle={(enabled) => handleUpdateFlag(buildUpdatePayload(detailsFlag, enabled), `Flag ${enabled ? "enabled" : "disabled"}.`, false)} onAddRule={() => openRuleForm()} onEditRule={openRuleForm} onDeleteRule={handleDeleteRule} onDeleteFlag={() => { setFlagDeleteError(""); setDeletingFlag(detailsFlag); }} />}
      {isEditOpen && detailsFlag && <FeatureFlagEditForm flag={detailsFlag} isSubmitting={isUpdating} submitError={updateError} onClose={() => { if (!isUpdating) { setIsEditOpen(false); setIsDetailsOpen(true); } }} onSubmit={(payload) => handleUpdateFlag(payload, "Flag changes saved.")} />}
      {isRuleFormOpen && detailsFlag && <TargetingRuleForm flag={detailsFlag} rule={editingRule} isSubmitting={isRuleSaving} submitError={ruleSubmitError} onClose={closeRuleForm} onSubmit={handleSaveRule} />}
      {deletingFlag && <DeleteFlagDialog flag={deletingFlag} isDeleting={isFlagDeleting} error={flagDeleteError} onClose={() => !isFlagDeleting && setDeletingFlag(null)} onConfirm={handleDeleteFlag} />}
    </section>
  );
}

export default FeaturesPage;
