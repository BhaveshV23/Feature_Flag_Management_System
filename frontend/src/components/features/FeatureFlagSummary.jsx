function FeatureFlagSummary({ total, enabled, disabled }) {
  return (
    <div className="feature-summary" aria-label="Filtered feature flag summary">
      <div><span>Showing</span><strong>{total}</strong><small>matching flags</small></div>
      <div><span>Enabled</span><strong className="summary-enabled">{enabled}</strong><small>matching flags</small></div>
      <div><span>Disabled</span><strong className="summary-disabled">{disabled}</strong><small>matching flags</small></div>
    </div>
  );
}

export default FeatureFlagSummary;
