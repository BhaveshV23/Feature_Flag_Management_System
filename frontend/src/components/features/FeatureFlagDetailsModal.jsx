import { useEffect, useRef } from "react";
import TargetingRulesPanel from "./TargetingRulesPanel";

function formatDate(value) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Not available" : date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function DetailRow({ label, children }) {
  return <div className="flag-detail-row"><dt>{label}</dt><dd>{children || "Not set"}</dd></div>;
}

function FeatureFlagDetailsModal({ flag, environmentName, isLoading, error, actionError, isSaving, targetingRules, isRulesLoading, rulesError, ruleActionError, isDeletingRule, onClose, onRetry, onRetryRules, onEdit, onToggle, onAddRule, onEditRule, onDeleteRule, onDeleteFlag }) {
  const closeButtonRef = useRef(null);

  useEffect(() => {
    closeButtonRef.current?.focus();
    const handleEscape = (event) => {
      if (event.key === "Escape" && !isSaving) onClose();
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isSaving, onClose]);

  const content = isLoading ? (
    <div className="flag-details-state" role="status"><span className="details-spinner" aria-hidden="true" /><p>Loading flag details…</p></div>
  ) : error ? (
    <div className="flag-details-state flag-details-error" role="alert"><h3>Unable to load this flag</h3><p>{error}</p><button className="btn secondary" onClick={onRetry} type="button">Try again</button></div>
  ) : !flag ? (
    <div className="flag-details-state" role="alert"><h3>Flag not found</h3><p>This flag may have been removed. Return to the feature flag list and try again.</p></div>
  ) : (
    <>
      <div className="flag-details-hero">
        <div><p className="dashboard-eyebrow">Feature flag</p><h2>{flag.name || "Unnamed flag"}</h2><code>{flag.key}</code></div>
        <span className={`flag-status ${flag.enabled ? "is-enabled" : "is-disabled"}`}>{flag.enabled ? "Enabled" : "Disabled"}</span>
      </div>
      {actionError && <div className="form-submit-error flag-details-submit-error" role="alert">{actionError}</div>}
      <section className="flag-details-section" aria-labelledby="flag-overview-heading"><h3 id="flag-overview-heading">Overview</h3><dl className="flag-details-grid"><DetailRow label="Environment">{environmentName || `Environment ${flag.environment_id}`}</DetailRow><DetailRow label="Owner team">{flag.owner_team}</DetailRow><DetailRow label="Description"><span className="flag-detail-description">{flag.description}</span></DetailRow></dl></section>
      <section className="flag-details-section" aria-labelledby="flag-configuration-heading"><h3 id="flag-configuration-heading">Configuration</h3><dl className="flag-details-grid"><DetailRow label="Type">{flag.type}</DetailRow><DetailRow label="Default value"><code>{flag.default_value ?? "Not set"}</code></DetailRow></dl></section>
      <TargetingRulesPanel rules={targetingRules} isLoading={isRulesLoading} error={rulesError} actionError={ruleActionError} isDeleting={isDeletingRule} onRetry={onRetryRules} onAdd={onAddRule} onEdit={onEditRule} onDelete={onDeleteRule} />
      <section className="flag-details-section" aria-labelledby="flag-metadata-heading"><h3 id="flag-metadata-heading">Metadata</h3><dl className="flag-details-grid"><DetailRow label="Created">{formatDate(flag.created_at)}</DetailRow><DetailRow label="Last updated">{formatDate(flag.updated_at)}</DetailRow></dl></section>
      <div className="flag-details-actions">
        <button className="btn secondary" disabled={isSaving} onClick={onEdit} type="button">Edit Flag</button>
        <button className={`btn ${flag.enabled ? "danger" : "primary"}`} disabled={isSaving} onClick={() => onToggle(!flag.enabled)} type="button">{isSaving ? "Saving…" : flag.enabled ? "Disable Flag" : "Enable Flag"}</button>
        <button className="text-action destructive flag-delete-action" disabled={isSaving} onClick={onDeleteFlag} type="button">Delete Flag</button>
      </div>
    </>
  );

  return (
    <div className="feature-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && !isSaving && onClose()}>
      <section className="feature-modal feature-details-modal" aria-labelledby="flag-details-title" aria-modal="true" role="dialog">
        <div className="feature-modal-header"><div><p className="dashboard-eyebrow">Release configuration</p><h2 id="flag-details-title">Flag details</h2></div><button ref={closeButtonRef} className="feature-modal-close" aria-label="Close flag details" disabled={isSaving} onClick={onClose} type="button">×</button></div>
        {content}
      </section>
    </div>
  );
}

export default FeatureFlagDetailsModal;
