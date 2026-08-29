import { useEffect, useState } from "react";

const initialValues = {
  environment_id: "",
  key: "",
  name: "",
  type: "boolean",
  default_value: "",
  enabled: true,
  description: "",
  owner_team: "",
};

function validate(values) {
  const errors = {};
  const keyPattern = /^[a-z0-9][a-z0-9_.-]*$/;

  if (!values.environment_id) errors.environment_id = "Select an environment.";
  if (!values.key.trim()) errors.key = "Enter a flag key.";
  else if (values.key.length > 100) errors.key = "Flag keys must be 100 characters or fewer.";
  else if (!keyPattern.test(values.key)) errors.key = "Use lowercase letters, numbers, dots, hyphens, or underscores.";
  if (!values.name.trim()) errors.name = "Enter a flag name.";
  else if (values.name.length > 100) errors.name = "Flag names must be 100 characters or fewer.";
  if (!values.type.trim()) errors.type = "Enter a flag type.";
  if (values.type === "number" && (values.default_value === "" || !Number.isFinite(Number(values.default_value)))) errors.default_value = "Enter a finite number.";
  if (!values.description.trim()) errors.description = "Enter a description.";
  if (!values.owner_team.trim()) errors.owner_team = "Enter an owner team.";

  return errors;
}

function FeatureFlagForm({ environments, selectedEnvironmentId, onSubmit, onClose, isSubmitting, submitError }) {
  const [values, setValues] = useState({ ...initialValues, environment_id: selectedEnvironmentId || String(environments[0]?.id || "") });
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
    if (Object.keys(errors).length > 0) return;

    onSubmit({
      ...values,
      environment_id: Number(values.environment_id),
      key: values.key.trim(),
      name: values.name.trim(),
      type: values.type.trim(),
      description: values.description.trim(),
      owner_team: values.owner_team.trim(),
    });
  };

  const fieldError = (field) => fieldErrors[field] ? <span className="form-field-error">{fieldErrors[field]}</span> : null;

  return (
    <div className="feature-modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && !isSubmitting && onClose()}>
      <section className="feature-modal" role="dialog" aria-modal="true" aria-labelledby="create-flag-title">
        <div className="feature-modal-header">
          <div><p className="dashboard-eyebrow">Release configuration</p><h2 id="create-flag-title">Create Flag</h2><p>Add a flag to one of your configured environments.</p></div>
          <button className="feature-modal-close" aria-label="Close create flag form" disabled={isSubmitting} onClick={onClose} type="button">×</button>
        </div>
        <form className="feature-flag-form" onSubmit={handleSubmit} noValidate>
          {submitError && <div className="form-submit-error" role="alert">{submitError}</div>}
          <div className="form-field full-width"><label htmlFor="create-environment">Environment</label><select id="create-environment" value={values.environment_id} onChange={(event) => updateField("environment_id", event.target.value)} aria-invalid={Boolean(fieldErrors.environment_id)} required><option value="">Select environment</option>{environments.map((environment) => <option key={environment.id} value={environment.id}>{environment.name}</option>)}</select>{fieldError("environment_id")}</div>
          <div className="form-field"><label htmlFor="create-flag-key">Key</label><input id="create-flag-key" value={values.key} onChange={(event) => updateField("key", event.target.value)} maxLength={100} placeholder="new_checkout" aria-invalid={Boolean(fieldErrors.key)} required />{fieldError("key")}</div>
          <div className="form-field"><label htmlFor="create-flag-name">Name</label><input id="create-flag-name" value={values.name} onChange={(event) => updateField("name", event.target.value)} maxLength={100} placeholder="New Checkout" aria-invalid={Boolean(fieldErrors.name)} required />{fieldError("name")}</div>
          <div className="form-field"><label htmlFor="create-flag-type">Type</label><select id="create-flag-type" value={values.type} onChange={(event) => updateField("type", event.target.value)} aria-invalid={Boolean(fieldErrors.type)} required><option value="boolean">boolean</option><option value="string">string</option><option value="number">number</option></select>{fieldError("type")}</div>
          <div className="form-field"><label htmlFor="create-default-value">Default Value</label><input id="create-default-value" type={values.type === "number" ? "number" : "text"} step={values.type === "number" ? "any" : undefined} value={values.default_value} onChange={(event) => updateField("default_value", event.target.value)} placeholder={values.type === "number" ? "0" : "false"} aria-invalid={Boolean(fieldErrors.default_value)} required />{fieldError("default_value")}</div>
          <div className="form-field"><label htmlFor="create-owner-team">Owner Team</label><input id="create-owner-team" value={values.owner_team} onChange={(event) => updateField("owner_team", event.target.value)} placeholder="platform" aria-invalid={Boolean(fieldErrors.owner_team)} required />{fieldError("owner_team")}</div>
          <div className="form-field full-width"><label htmlFor="create-description">Description</label><textarea id="create-description" value={values.description} onChange={(event) => updateField("description", event.target.value)} rows="3" placeholder="Describe when this flag should be used." aria-invalid={Boolean(fieldErrors.description)} required />{fieldError("description")}</div>
          <label className="enabled-field"><input type="checkbox" checked={values.enabled} onChange={(event) => updateField("enabled", event.target.checked)} /> Enabled on creation</label>
          <div className="feature-form-actions"><button className="btn secondary" disabled={isSubmitting} onClick={onClose} type="button">Cancel</button><button className="btn primary" disabled={isSubmitting} type="submit">{isSubmitting ? "Creating..." : "Create Flag"}</button></div>
        </form>
      </section>
    </div>
  );
}

export default FeatureFlagForm;
