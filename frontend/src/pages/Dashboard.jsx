import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAuditLogs, getEnvironments, getFlags, getTargetingRules } from "../services/api";
import StatCard from "../components/dashboard/StatCard";

function Dashboard() {
  const [flags, setFlags] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [targetingRules, setTargetingRules] = useState([]);
  const [auditRecords, setAuditRecords] = useState([]);
  const [isAuditLoading, setIsAuditLoading] = useState(true);
  const [auditError, setAuditError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isCurrent = true;

    async function loadDashboardData() {
      setIsLoading(true);
      setError("");

      try {
        const [flagResult, environmentResult, targetingRuleResult] = await Promise.all([getFlags(), getEnvironments(), getTargetingRules()]);
        if (isCurrent) {
          setFlags(Array.isArray(flagResult) ? flagResult : []);
          setEnvironments(Array.isArray(environmentResult) ? environmentResult : []);
          setTargetingRules(Array.isArray(targetingRuleResult) ? targetingRuleResult : []);
        }
      } catch (requestError) {
        if (isCurrent) {
          setError(requestError.message || "Unable to load dashboard data.");
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    async function loadAuditActivity() {
      try {
        const auditResult = await getAuditLogs();
        if (isCurrent) setAuditRecords(Array.isArray(auditResult) ? auditResult : []);
      } catch (requestError) {
        if (isCurrent) setAuditError(requestError.message || "Recent activity is unavailable.");
      } finally {
        if (isCurrent) setIsAuditLoading(false);
      }
    }

    loadDashboardData();
    loadAuditActivity();
    return () => { isCurrent = false; };
  }, []);

  if (isLoading) {
    return <section className="dashboard-state" role="status"><div className="dashboard-state-mark" aria-hidden="true">◌</div><h2>Loading workspace data</h2><p>Fetching your feature flags and environments.</p></section>;
  }

  if (error) {
    return <section className="dashboard-state dashboard-state-error" role="alert"><div className="dashboard-state-mark" aria-hidden="true">!</div><h2>We could not load the workspace</h2><p>{error}</p></section>;
  }

  const enabledFlags = flags.filter((flag) => flag.enabled).length;
  const disabledFlags = flags.length - enabledFlags;
  const environmentStatus = environments.map((environment) => {
    const environmentFlags = flags.filter((flag) => flag.environment_id === environment.id);
    return { ...environment, flagCount: environmentFlags.length, enabledCount: environmentFlags.filter((flag) => flag.enabled).length };
  });
  const activeRules = targetingRules.filter((rule) => rule.is_active).length;
  const inactiveRules = targetingRules.length - activeRules;
  const rolloutRules = targetingRules.filter((rule) => rule.rule_type === "percentage");
  const flagById = new Map(flags.map((flag) => [flag.id, flag]));
  const environmentById = new Map(environments.map((environment) => [environment.id, environment]));
  const recentChanges = [...auditRecords].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)).slice(0, 5);
  const formatActivityDate = (value) => { if (!value) return "Not available"; const parsed = new Date(value); return Number.isNaN(parsed.getTime()) ? "Not available" : parsed.toLocaleDateString(undefined, { month: "short", day: "numeric" }); };

  return (
    <section className="dashboard-overview">
      <div className="overview-hero">
        <div className="overview-hero-copy"><p className="dashboard-eyebrow">Release control center</p><h2>Ship features with confidence.</h2><p>Monitor your feature configuration, rollouts, environments, and recent workspace activity — all in one place.</p></div>
        <div className="overview-hero-visual" aria-hidden="true"><div className="hero-grid-lines" /><div className="hero-node hero-node-one" /><div className="hero-node hero-node-two" /><div className="hero-node hero-node-three" /><div className="hero-console"><div><span className="hero-console-dot" /><span className="hero-console-dot" /><span className="hero-console-dot" /></div><strong>RELEASE / 04</strong><div className="hero-console-row"><span>production</span><b>75%</b></div><div className="hero-console-progress"><i /></div><div className="hero-console-row"><span>staging</span><b>active</b></div></div></div>
      </div>
      {flags.length === 0 && environments.length === 0 ? (
        <div className="overview-empty-state dashboard-data-empty">
          <div className="empty-state-mark" aria-hidden="true">◈</div>
          <h3>Your workspace is ready for its first configuration</h3>
          <p>No flags or environments are available yet. Add them through the management areas when they are ready.</p>
        </div>
      ) : (
        <>
          <div className="dashboard-stats-grid"><StatCard label="Total Flags" value={flags.length} detail="Configured across your workspace" tone="blue" /><StatCard label="Enabled Flags" value={enabledFlags} detail="Currently active configurations" tone="green" /><StatCard label="Disabled Flags" value={disabledFlags} detail="Available for future releases" tone="muted" /><StatCard label="Environments" value={environments.length} detail="Configured release contexts" tone="purple" /></div>
          <div className="overview-operational-grid">
            <section className="overview-panel overview-activity-panel">
              <div className="overview-panel-heading"><div><p className="dashboard-eyebrow">Workspace activity</p><h3>Recent Flag Changes</h3></div><Link className="text-action" to="/audit-logs">View all audit logs →</Link></div>
              {isAuditLoading ? <p className="overview-panel-state" role="status">Loading recent activity…</p> : auditError ? <p className="overview-panel-state overview-panel-error" role="status">Recent activity is currently unavailable.</p> : !recentChanges.length ? <p className="overview-panel-state">No recorded flag changes yet.</p> : <div className="overview-activity-list">{recentChanges.map((record) => { const flag = flagById.get(record.flag_id); return <article className="overview-activity-item" key={record.id}><span className="audit-action">{record.action?.replace("TARGETING_RULE_", "Rule ") || "Activity"}</span><div><strong>{flag?.name || (record.flag_id ? `Flag #${record.flag_id}` : "Environment activity")}</strong><span>{environmentById.get(record.environment_id)?.name || `Environment #${record.environment_id}`} · {record.actor} · {formatActivityDate(record.created_at)}</span></div></article>; })}</div>}
            </section>
            <section className="overview-panel overview-rollout-panel">
              <div className="overview-panel-heading"><div><p className="dashboard-eyebrow">Release control</p><h3>Rollout Summary</h3></div><Link className="text-action" to="/rollouts">View all rollouts →</Link></div>
              {!rolloutRules.length ? <p className="overview-panel-state">No percentage rollouts configured yet.</p> : <div className="overview-rollout-list">{rolloutRules.slice(0, 5).map((rule) => { const flag = flagById.get(rule.flag_id); const environment = environmentById.get(flag?.environment_id); const percentage = Math.max(0, Math.min(100, Number(rule.percentage) || 0)); return <article className="overview-rollout-item" key={rule.id}><div><strong>{flag?.name || `Flag #${rule.flag_id}`}</strong><span>{environment?.name || "Environment unavailable"}</span><div className="overview-rollout-progress" aria-hidden="true"><i style={{ "--rollout-width": `${percentage}%` }} /></div></div><b>{percentage}%</b></article>; })}</div>}
            </section>
          </div>
          <section className="overview-panel overview-environment-panel"><div className="overview-panel-heading"><div><p className="dashboard-eyebrow">Workspace configuration</p><h3>Environment Status</h3><p>Configured feature flags grouped by release environment.</p></div><Link className="text-action" to="/environments">View environments →</Link></div>{!environmentStatus.length ? <p className="overview-panel-state">No environments configured yet.</p> : <div className="overview-environment-list">{environmentStatus.map((environment) => <div className="overview-environment-item" key={environment.id}><div><strong>{environment.name}</strong><span>{environment.enabledCount} enabled · {environment.flagCount - environment.enabledCount} disabled</span></div><b>{environment.flagCount} {environment.flagCount === 1 ? "flag" : "flags"}</b></div>)}</div>}</section>
          <section className="overview-panel overview-health-panel"><div className="overview-panel-heading"><div><p className="dashboard-eyebrow">Configuration posture</p><h3>Configuration Health</h3><p>Current release configuration across the workspace.</p></div><Link className="text-action" to="/analytics">Explore analytics →</Link></div><div className="overview-health-grid"><div><strong>{enabledFlags}</strong><span>Enabled flags</span></div><div><strong>{disabledFlags}</strong><span>Disabled flags</span></div><div><strong>{activeRules}</strong><span>Active rules</span></div><div><strong>{inactiveRules}</strong><span>Inactive rules</span></div><div><strong>{rolloutRules.length}</strong><span>Percentage rollouts</span></div></div></section>
        </>
      )}
    </section>
  );
}

export default Dashboard;
