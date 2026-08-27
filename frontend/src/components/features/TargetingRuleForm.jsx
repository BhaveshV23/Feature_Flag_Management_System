import { useEffect, useState } from "react";

function initialValues(rule) {
  return { rule_type: rule?.rule_type || "user", priority: String(rule?.priority || 1), value: rule?.value ?? "", percentage: String(rule?.percentage ?? 50), enabled: rule?.enabled ?? true, is_active: rule?.is_active ?? true };
}

function TargetingRuleForm({ flag, rule, isSubmitting, submitError, onClose, onSubmit }) {
  const [values, setValues] = useState(() => initialValues(rule));
  const [errors, setErrors] = useState({});
  const isPercentage = values.rule_type === "percentage";

  useEffect(() => {
    const handleEscape = (event) => { if (event.key === "Escape" && !isSubmitting) onClose(); };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isSubmitting, onClose]);

  const update = (field, value) => { setValues((current) => ({ ...current, [field]: value })); setErrors((current) => ({ ...current, [field]: "" })); };
  const changeType = (rule_type) => setValues((current) => ({ ...current, rule_type, value: rule_type === "percentage" ? "" : current.rule_type === "percentage" ? "" : current.value, percentage: rule_type === "percentage" ? current.percentage || "50" : "" }));
  const submit = (event) => {
    event.preventDefault();
    const nextErrors = {};
    const priority = Number(values.priority);
    const percentage = Number(values.percentage);
    if (!Number.isInteger(priority) || priority < 1) nextErrors.priority = "Priority must be a whole number of 1 or greater.";
    if (!isPercentage && !values.value.trim()) nextErrors.value = values.rule_type === "group" ? "Enter a group name." : "Enter a user ID.";
    if (isPercentage && (!Number.isInteger(percentage) || percentage < 0 || percentage > 100)) nextErrors.percentage = "Enter a whole percentage from 0 to 100.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;
    onSubmit({ flag_id: flag.id, priority, rule_type: values.rule_type, operator: isPercentage ? null : "equals", value: isPercentage ? null : values.value.trim(), percentage: isPercentage ? percentage : null, enabled: values.enabled, is_active: values.is_active });
  };

  return <div className="feature-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && !isSubmitting && onClose()}>
    <section className="feature-modal targeting-form-modal" aria-labelledby="targeting-rule-title" aria-modal="true" role="dialog">
      <div className="feature-modal-header"><div><p className="dashboard-eyebrow">Release configuration</p><h2 id="targeting-rule-title">{rule ? "Edit Targeting Rule" : "Add Targeting Rule"}</h2><p>{flag.name} <code>{flag.key}</code></p></div><button className="feature-modal-close" aria-label="Close targeting rule form" disabled={isSubmitting} onClick={onClose} type="button">×</button></div>
      <form className="feature-flag-form targeting-rule-form" noValidate onSubmit={submit}>
        {submitError && <div className="form-submit-error" role="alert">{submitError}</div>}
        <div className="form-field full-width"><label htmlFor="rule-type">Rule type</label><select id="rule-type" value={values.rule_type} onChange={(event) => changeType(event.target.value)}><option value="user">User targeting</option><option value="group">Group targeting</option><option value="percentage">Percentage rollout</option></select></div>
        {isPercentage ? <div className="form-field full-width percentage-rollout-field"><div className="percentage-field-heading"><label htmlFor="rule-percentage">Percentage rollout</label><output htmlFor="rule-percentage">{Math.max(0, Math.min(100, Number(values.percentage) || 0))}%</output></div><input id="rule-percentage" aria-describedby="rule-percentage-hint" aria-invalid={Boolean(errors.percentage)} max="100" min="0" onChange={(event) => update("percentage", event.target.value)} type="range" value={Math.max(0, Math.min(100, Number(values.percentage) || 0))} /><div className="percentage-number-row"><input aria-label="Percentage rollout value" max="100" min="0" onChange={(event) => update("percentage", event.target.value)} type="number" value={values.percentage} /><span id="rule-percentage-hint">Choose the percentage of identified users who receive this treatment.</span></div>{errors.percentage && <span className="form-field-error">{errors.percentage}</span>}</div> : <div className="form-field full-width"><label htmlFor="rule-value">{values.rule_type === "group" ? "Group name" : "User ID"}</label><input id="rule-value" value={values.value} onChange={(event) => update("value", event.target.value)} placeholder={values.rule_type === "group" ? "beta-testers" : "user-123"} aria-invalid={Boolean(errors.value)} required />{errors.value && <span className="form-field-error">{errors.value}</span>}<span className="form-field-hint">Matches using the equals operator.</span></div>}
        <div className="form-field"><label htmlFor="rule-priority">Priority</label><input id="rule-priority" min="1" value={values.priority} onChange={(event) => update("priority", event.target.value)} type="number" aria-invalid={Boolean(errors.priority)} required />{errors.priority && <span className="form-field-error">{errors.priority}</span>}<span className="form-field-hint">Lower numbers are evaluated first within this rule type.</span></div>
        <fieldset className="treatment-field"><legend>Treatment</legend><div className="segmented-control"><label><input checked={values.enabled} name="treatment" onChange={() => update("enabled", true)} type="radio" /><span>Enabled</span></label><label><input checked={!values.enabled} name="treatment" onChange={() => update("enabled", false)} type="radio" /><span>Disabled</span></label></div></fieldset>
        <label className="rule-active-control"><span><strong>Rule status</strong><small>Active rules participate in evaluation.</small></span><input checked={values.is_active} onChange={(event) => update("is_active", event.target.checked)} type="checkbox" /><i aria-hidden="true" /></label>
        <div className="feature-form-actions"><button className="btn secondary" disabled={isSubmitting} onClick={onClose} type="button">Cancel</button><button className="btn primary" disabled={isSubmitting} type="submit">{isSubmitting ? "Saving…" : rule ? "Save Rule" : "Add Rule"}</button></div>
      </form>
    </section>
  </div>;
}

export default TargetingRuleForm;
