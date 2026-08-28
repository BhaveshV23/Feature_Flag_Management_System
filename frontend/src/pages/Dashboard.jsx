import { useEffect, useState } from "react";
import { getEnvironments, getFlags, getTargetingRules } from "../services/api";
import FlagStatusChart from "../components/dashboard/FlagStatusChart";
import FlagTypesChart from "../components/dashboard/FlagTypesChart";
import FlagsByEnvironmentChart from "../components/dashboard/FlagsByEnvironmentChart";
import StatCard from "../components/dashboard/StatCard";
import TargetingRulesChart from "../components/dashboard/TargetingRulesChart";

function Dashboard() {
  const [flags, setFlags] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [targetingRules, setTargetingRules] = useState([]);
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

    loadDashboardData();
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
  const flagsByEnvironment = environments.map((environment) => ({
    environment: environment.name,
    flags: flags.filter((flag) => flag.environment_id === environment.id).length,
  }));
  const environmentIds = new Set(environments.map((environment) => environment.id));
  const unknownEnvironmentCounts = flags.reduce((counts, flag) => {
    if (!environmentIds.has(flag.environment_id)) {
      counts[flag.environment_id] = (counts[flag.environment_id] || 0) + 1;
    }
    return counts;
  }, {});
  Object.entries(unknownEnvironmentCounts).forEach(([environmentId, count]) => {
    flagsByEnvironment.push({ environment: `Environment ${environmentId}`, flags: count });
  });
  const typeCounts = flags.reduce((counts, flag) => {
    const type = flag.type || "Unspecified";
    counts[type] = (counts[type] || 0) + 1;
    return counts;
  }, {});
  const flagTypes = Object.entries(typeCounts).map(([type, count]) => ({ type, flags: count }));
  const statusData = [
    { name: "Enabled", value: enabledFlags },
    { name: "Disabled", value: disabledFlags },
  ].filter((entry) => entry.value > 0);
  const targetingRuleCounts = Object.entries(targetingRules.reduce((counts, rule) => {
    const type = rule.rule_type || "Unspecified";
    counts[type] = (counts[type] || 0) + 1;
    return counts;
  }, {})).map(([type, rules]) => ({ type, rules }));

  return (
    <section className="dashboard-overview">
      <div className="overview-intro">
        <p className="dashboard-eyebrow">Release control center</p>
        <h2>Build safer releases, one decision at a time.</h2>
        <p>Your workspace at a glance, based on the feature flags and environments currently configured.</p>
      </div>
      {flags.length === 0 && environments.length === 0 ? (
        <div className="overview-empty-state dashboard-data-empty">
          <div className="empty-state-mark" aria-hidden="true">◈</div>
          <h3>Your workspace is ready for its first configuration</h3>
          <p>No flags or environments are available yet. Add them through the management areas when they are ready.</p>
        </div>
      ) : (
        <>
          <div className="dashboard-stats-grid">
            <StatCard label="Total Flags" value={flags.length} detail="Configured across your workspace" tone="blue" />
            <StatCard label="Enabled Flags" value={enabledFlags} detail="Currently active configurations" tone="green" />
            <StatCard label="Disabled Flags" value={disabledFlags} detail="Available for future releases" tone="muted" />
            <StatCard label="Environments" value={environments.length} detail="Configured release contexts" tone="purple" />
          </div>
          <div className="dashboard-chart-grid dashboard-chart-grid-top">
            <FlagStatusChart data={statusData} />
            <FlagsByEnvironmentChart data={flagsByEnvironment} />
          </div>
          <div className="dashboard-chart-grid">
            <FlagTypesChart data={flagTypes} />
            <TargetingRulesChart data={targetingRuleCounts} />
          </div>
        </>
      )}
    </section>
  );
}

export default Dashboard;
