import { useEffect, useState } from "react";

function validate(values) {
  const errors = {};
  const keyPattern = /^[a-z0-9][a-z0-9_.-]*$/;
  if (!values.key.trim()) errors.key = "Enter a flag key.";
  else if (values.key.length > 100) errors.key = "Flag keys must be 100 characters or fewer.";
  else if (!keyPattern.test(values.key)) errors.key = "Use lowercase letters, numbers, dots, hyphens, or underscores.";
  if (!values.type.trim()) errors.type = "Enter a flag type.";
  if (!values.description.trim()) errors.description = "Enter a description.";
  if (!values.owner_team.trim()) errors.owner_team = "Enter an owner team.";
  return errors;
}

function FeatureFlagEditForm({ flag, isSubmitting, submitError, onClose, onSubmit }) {
  const [values, setValues] = useState(() => ({ key: flag.key || "", type: flag.type || "", default_value: flag.default_value ?? "", enabled: Boolean(flag.enabled), description: flag.description || "", owner_team: flag.owner_team || "" }));
  const [fieldErrors, setFieldErrors] = useState({});

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === "Escape" && !isSubmitting) onClose();
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isSubmitting, onClose]);

  const updateField = (field, value) => {
    setValues((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => ({ ...current, [field]: "" }));
  };
  const handleSubmit = (event) => {
    event.preventDefault();
    const errors = validate(values);
    setFieldErrors(errors);
    if (Object.keys(errors).length) return;
    onSubmit({ ...values, key: values.key.trim(), type: values.type.trim(), description: values.description.trim(), owner_team: values.owner_team.trim() });
  };
  const fieldError = (field) => fieldErrors[field] ? <span className="form-field-error">{fieldErrors[field]}</span> : null;

  return (
    <div className="feature-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && !isSubmitting && onClose()}>
      <section className="feature-modal" aria-labelledby="edit-flag-title" aria-modal="true" role="dialog">
        <div className="feature-modal-header"><div><p className="dashboard-eyebrow">Release configuration</p><h2 id="edit-flag-title">Edit Flag</h2><p>Update the configuration supported by this environment’s flag API.</p></div><button className="feature-modal-close" aria-label="Close edit flag form" disabled={isSubmitting} onClick={onClose} type="button">×</button></div>
        <form className="feature-flag-form" noValidate onSubmit={handleSubmit}>
          {submitError && <div className="form-submit-error" role="alert">{submitError}</div>}
          <div className="form-field"><label htmlFor="edit-flag-key">Key</label><input id="edit-flag-key" value={values.key} onChange={(event) => updateField("key", event.target.value)} maxLength={100} aria-invalid={Boolean(fieldErrors.key)} required />{fieldError("key")}</div>
          <div className="form-field"><label htmlFor="edit-flag-type">Type</label><input id="edit-flag-type" value={values.type} onChange={(event) => updateField("type", event.target.value)} aria-invalid={Boolean(fieldErrors.type)} required />{fieldError("type")}</div>
          <div className="form-field"><label htmlFor="edit-default-value">Default Value</label><input id="edit-default-value" value={values.default_value} onChange={(event) => updateField("default_value", event.target.value)} required /></div>
          <div className="form-field"><label htmlFor="edit-owner-team">Owner Team</label><input id="edit-owner-team" value={values.owner_team} onChange={(event) => updateField("owner_team", event.target.value)} aria-invalid={Boolean(fieldErrors.owner_team)} required />{fieldError("owner_team")}</div>
          <div className="form-field full-width"><label htmlFor="edit-description">Description</label><textarea id="edit-description" value={values.description} onChange={(event) => updateField("description", event.target.value)} rows="3" aria-invalid={Boolean(fieldErrors.description)} required />{fieldError("description")}</div>
          <label className="enabled-field"><input type="checkbox" checked={values.enabled} onChange={(event) => updateField("enabled", event.target.checked)} /> Enabled</label>
          <p className="edit-flag-note">Name and environment cannot be changed through the current update API.</p>
          <div className="feature-form-actions"><button className="btn secondary" disabled={isSubmitting} onClick={onClose} type="button">Cancel</button><button className="btn primary" disabled={isSubmitting} type="submit">{isSubmitting ? "Saving…" : "Save Changes"}</button></div>
        </form>
      </section>
    </div>
  );
}

export default FeatureFlagEditForm;
