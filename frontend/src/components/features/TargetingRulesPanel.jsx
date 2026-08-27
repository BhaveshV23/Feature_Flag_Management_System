import TargetingRuleList from "./TargetingRuleList";

function TargetingRulesPanel({ rules, isLoading, error, actionError, isDeleting, onRetry, onAdd, onEdit, onDelete }) {
  return <section className="flag-details-section targeting-section" aria-labelledby="targeting-rules-heading">
    <div className="targeting-section-heading"><div><h3 id="targeting-rules-heading">Targeting Rules</h3><p>Define who receives this feature.</p></div><button className="btn secondary targeting-add-button" disabled={isLoading || isDeleting} onClick={onAdd} type="button">+ Add Rule</button></div>
    {isLoading ? <div className="targeting-panel-state" role="status"><span className="details-spinner" aria-hidden="true" /><span>Loading targeting rules…</span></div> : error ? <div className="targeting-panel-state targeting-panel-error" role="alert"><span>Unable to load targeting rules.</span><button className="text-action" onClick={onRetry} type="button">Retry</button></div> : <>{actionError && <div className="form-submit-error targeting-action-error" role="alert">{actionError}</div>}<TargetingRuleList rules={rules} isDeleting={isDeleting} onEdit={onEdit} onDelete={onDelete} /></>}
  </section>;
}

export default TargetingRulesPanel;
