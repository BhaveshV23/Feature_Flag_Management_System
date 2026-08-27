import { useState } from "react";

function ruleCondition(rule) {
  if (rule.rule_type === "percentage") return `${rule.percentage ?? 0}% of users`;
  return `${rule.rule_type === "group" ? "group" : "user ID"} equals “${rule.value ?? ""}”`;
}

function TargetingRuleList({ rules, isDeleting, onEdit, onDelete }) {
  const [confirmingRuleId, setConfirmingRuleId] = useState(null);

  if (!rules.length) {
    return <div className="targeting-empty"><strong>No targeting rules configured</strong><span>Add your first rule to define who receives this feature.</span></div>;
  }

  return <div className="targeting-rule-list">
    {rules.map((rule) => {
      const isConfirming = confirmingRuleId === rule.id;
      return (
        <article className="targeting-rule-card" key={rule.id}>
          <div className="targeting-rule-topline"><span className="targeting-rule-type">{rule.rule_type === "percentage" ? "Percentage rollout" : `${rule.rule_type} targeting`}</span><span className={`targeting-status ${rule.is_active ? "is-active" : "is-inactive"}`}>{rule.is_active ? "Active" : "Inactive"}</span></div>
          <p className="targeting-condition">{ruleCondition(rule)}</p>
          {rule.rule_type === "percentage" && <div className="targeting-progress" aria-label={`${rule.percentage ?? 0}% rollout`}><span style={{ width: `${Math.max(0, Math.min(100, Number(rule.percentage) || 0))}%` }} /></div>}
          <div className="targeting-rule-meta"><div><span>Treatment</span><strong className={rule.enabled ? "is-treatment-enabled" : "is-treatment-disabled"}>{rule.enabled ? "Enabled" : "Disabled"}</strong></div><div><span>Priority</span><strong>{rule.priority}</strong></div></div>
          {isConfirming ? (
            <div className="targeting-delete-confirm" role="alert"><span>Delete this targeting rule? This cannot be undone.</span><div><button className="text-action" disabled={isDeleting} onClick={() => setConfirmingRuleId(null)} type="button">Cancel</button><button className="text-action destructive" disabled={isDeleting} onClick={() => onDelete(rule.id)} type="button">{isDeleting ? "Deleting…" : "Delete rule"}</button></div></div>
          ) : <div className="targeting-rule-actions"><button className="text-action" disabled={isDeleting} onClick={() => onEdit(rule)} type="button">Edit</button><button className="text-action destructive" disabled={isDeleting} onClick={() => setConfirmingRuleId(rule.id)} type="button">Delete</button></div>}
        </article>
      );
    })}
  </div>;
}

export default TargetingRuleList;
