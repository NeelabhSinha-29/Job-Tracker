"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type SummaryReport = {
  total_jobs: number;
  total_applications: number;
  jobs_without_application_record: number;
  active_applications: number;
  unique_companies: number;
  total_keywords: number;
  upcoming_deadlines: number;
  overdue_deadlines: number;
};

type CountByLabel = {
  label: string;
  count: number;
};

type SalarySummary = {
  jobs_with_salary_min: number;
  jobs_with_salary_max: number;
  average_salary_min: number | null;
  average_salary_max: number | null;
  lowest_salary_min: number | null;
  highest_salary_max: number | null;
};

type Job = {
  job_id: number;
  company_name: string;
  job_title: string;
  application_deadline: string | null;
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function DashboardPage() {
  const [summary, setSummary] = useState<SummaryReport | null>(null);
  const [jobsByStatus, setJobsByStatus] = useState<CountByLabel[]>([]);
  const [jobsByCompany, setJobsByCompany] = useState<CountByLabel[]>([]);
  const [salarySummary, setSalarySummary] = useState<SalarySummary | null>(null);
  const [upcomingDeadlines, setUpcomingDeadlines] = useState<Job[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadReports() {
      setIsLoading(true);
      setError(null);

      try {
        const [summaryResponse, statusResponse, companyResponse, salaryResponse, deadlinesResponse] =
          await Promise.all([
            fetch(`${apiBaseUrl}/reports/summary`, { cache: "no-store" }),
            fetch(`${apiBaseUrl}/reports/jobs-by-status`, { cache: "no-store" }),
            fetch(`${apiBaseUrl}/reports/jobs-by-company`, { cache: "no-store" }),
            fetch(`${apiBaseUrl}/reports/salary-summary`, { cache: "no-store" }),
            fetch(`${apiBaseUrl}/reports/upcoming-deadlines?limit=8`, {
              cache: "no-store",
            }),
          ]);

        if (!summaryResponse.ok) {
          throw new Error(`GET /reports/summary failed with ${summaryResponse.status}`);
        }
        if (!statusResponse.ok) {
          throw new Error(
            `GET /reports/jobs-by-status failed with ${statusResponse.status}`,
          );
        }
        if (!companyResponse.ok) {
          throw new Error(
            `GET /reports/jobs-by-company failed with ${companyResponse.status}`,
          );
        }
        if (!salaryResponse.ok) {
          throw new Error(
            `GET /reports/salary-summary failed with ${salaryResponse.status}`,
          );
        }
        if (!deadlinesResponse.ok) {
          throw new Error(
            `GET /reports/upcoming-deadlines failed with ${deadlinesResponse.status}`,
          );
        }

        setSummary((await summaryResponse.json()) as SummaryReport);
        setJobsByStatus((await statusResponse.json()) as CountByLabel[]);
        setJobsByCompany((await companyResponse.json()) as CountByLabel[]);
        setSalarySummary((await salaryResponse.json()) as SalarySummary);
        setUpcomingDeadlines((await deadlinesResponse.json()) as Job[]);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Could not load dashboard data.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadReports();
  }, []);

  return (
    <main className="app-shell dashboard-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Local AI Job Tracker</p>
          <h1>Dashboard</h1>
          <p className="dashboard-intro">
            A quick view of your job search activity, application status, and deadlines.
          </p>
        </div>
        <div className="header-actions">
          <Link className="secondary-button" href="/">
            Jobs
          </Link>
        </div>
      </header>

      {isLoading ? <p className="state-text">Loading reports...</p> : null}
      {error ? <p className="message error">{error}</p> : null}

      {!isLoading && !error && summary ? (
        <section className="metric-grid">
          <MetricCard label="Jobs" value={summary.total_jobs} />
          <MetricCard label="Applications" value={summary.total_applications} />
          <MetricCard label="Active applications" value={summary.active_applications} />
          <MetricCard label="Companies" value={summary.unique_companies} />
          <MetricCard label="Keywords" value={summary.total_keywords} />
          <MetricCard label="Upcoming deadlines" value={summary.upcoming_deadlines} />
        </section>
      ) : null}

      {!isLoading && !error && summary && salarySummary ? (
        <section className="workspace-grid dashboard-grid">
          <section className="jobs-panel dashboard-panel">
            <div className="section-heading table-heading">
              <div>
                <h2>Salary snapshot</h2>
                <p>Quick aggregate view across saved jobs.</p>
              </div>
            </div>
            <div className="dashboard-section-body">
              <dl className="salary-grid">
                <SummaryPair
                  label="Jobs with min salary"
                  value={String(salarySummary.jobs_with_salary_min)}
                />
                <SummaryPair
                  label="Jobs with max salary"
                  value={String(salarySummary.jobs_with_salary_max)}
                />
                <SummaryPair
                  label="Average min"
                  value={formatCurrency(salarySummary.average_salary_min)}
                />
                <SummaryPair
                  label="Average max"
                  value={formatCurrency(salarySummary.average_salary_max)}
                />
                <SummaryPair
                  label="Lowest min"
                  value={formatCurrency(salarySummary.lowest_salary_min)}
                />
                <SummaryPair
                  label="Highest max"
                  value={formatCurrency(salarySummary.highest_salary_max)}
                />
              </dl>
            </div>
          </section>

          <section className="jobs-panel dashboard-panel">
            <div className="section-heading table-heading">
              <div>
                <h2>Upcoming deadlines</h2>
                <p>Next applications due soonest.</p>
              </div>
            </div>
            <div className="dashboard-section-body">
              {upcomingDeadlines.length > 0 ? (
                <ul className="report-list">
                  {upcomingDeadlines.map((job) => (
                    <li key={job.job_id} className="report-row">
                      <div>
                        <strong>{job.job_title}</strong>
                        <p>{job.company_name}</p>
                      </div>
                      <span>{formatDate(job.application_deadline)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="state-text">No upcoming deadlines found.</p>
              )}
            </div>
          </section>
        </section>
      ) : null}

      {!isLoading && !error ? (
        <section className="workspace-grid dashboard-grid">
          <section className="jobs-panel dashboard-panel">
            <div className="section-heading table-heading">
              <div>
                <h2>Application status</h2>
                <p>How the pipeline is currently distributed.</p>
              </div>
            </div>
            <div className="dashboard-section-body">
              <ul className="report-list">
                {jobsByStatus.map((item) => (
                  <li key={item.label} className="report-row">
                    <span>{item.label}</span>
                    <strong>{item.count}</strong>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <section className="jobs-panel dashboard-panel">
            <div className="section-heading table-heading">
              <div>
                <h2>Top companies</h2>
                <p>Most saved jobs by employer.</p>
              </div>
            </div>
            <div className="dashboard-section-body">
              <ul className="report-list">
                {jobsByCompany.slice(0, 8).map((item) => (
                  <li key={item.label} className="report-row">
                    <span>{item.label}</span>
                    <strong>{item.count}</strong>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        </section>
      ) : null}
    </main>
  );
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <article className="metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}

function SummaryPair({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function formatCurrency(value: number | null) {
  if (value === null || Number.isNaN(value)) {
    return "-";
  }

  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDate(value: string | null) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}
