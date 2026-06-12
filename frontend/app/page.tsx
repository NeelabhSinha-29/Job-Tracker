"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Job = {
  job_id: number;
  company_name: string;
  job_title: string;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  job_description: string;
  source_url: string | null;
  application_deadline: string | null;
  date_found: string;
  application?: {
    status: string;
  } | null;
};

type JobFormState = {
  company_name: string;
  job_title: string;
  location: string;
  salary_min: string;
  salary_max: string;
  job_description: string;
  source_url: string;
  application_deadline: string;
};

type DescriptionAnalysis = {
  summary: string;
  suggested_keywords: Array<{
    keyword: string;
    confidence: number;
  }>;
  seniority: string;
  score: number;
};

const initialFormState: JobFormState = {
  company_name: "",
  job_title: "",
  location: "",
  salary_min: "",
  salary_max: "",
  job_description: "",
  source_url: "",
  application_deadline: "",
};

const demoFormState: JobFormState = {
  company_name: "Northstar Analytics",
  job_title: "Senior Data Analyst",
  location: "Remote",
  salary_min: "65000",
  salary_max: "85000",
  job_description:
    "We are hiring a Senior Data Analyst to build dashboards, work with SQL and Python, and turn messy datasets into clear decisions. Experience with Tableau, stakeholder communication, and reporting automation is preferred.",
  source_url: "https://example.com/demo-job",
  application_deadline: "2026-07-31",
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";
const apiKey = process.env.NEXT_PUBLIC_API_KEY ?? "";

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [form, setForm] = useState<JobFormState>(initialFormState);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<DescriptionAnalysis | null>(null);

  const sortedJobs = useMemo(
    () =>
      [...jobs].sort((a, b) => {
        return b.job_id - a.job_id;
      }),
    [jobs],
  );

  const fetchJobs = useCallback(async () => {
    setIsLoadingJobs(true);
    setJobsError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/jobs`, {
        cache: "no-store",
        headers: createHeaders(),
      });

      if (!response.ok) {
        throw new Error(`GET /jobs failed with ${response.status}`);
      }

      const data = (await response.json()) as Job[];
      setJobs(data);
    } catch (error) {
      setJobsError(
        error instanceof Error ? error.message : "Could not load saved jobs.",
      );
    } finally {
      setIsLoadingJobs(false);
    }
  }, []);

  useEffect(() => {
    void fetchJobs();
  }, [fetchJobs]);

  function updateField(field: keyof JobFormState, value: string) {
    setForm((currentForm) => ({
      ...currentForm,
      [field]: value,
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    const payload = {
      company_name: form.company_name.trim(),
      job_title: form.job_title.trim(),
      location: emptyToNull(form.location),
      salary_min: numberOrNull(form.salary_min),
      salary_max: numberOrNull(form.salary_max),
      job_description: form.job_description.trim(),
      source_url: emptyToNull(form.source_url),
      application_deadline: emptyToNull(form.application_deadline),
    };

    try {
      const response = await fetch(`${apiBaseUrl}/jobs`, {
        method: "POST",
        headers: createHeaders(true),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const responseText = await response.text();
        throw new Error(responseText || `POST /jobs failed with ${response.status}`);
      }

      setForm(initialFormState);
      setSubmitSuccess("Job saved.");
      await fetchJobs();
    } catch (error) {
      setSubmitError(
        error instanceof Error ? error.message : "Could not save this job.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleAnalyzeDescription() {
    await analyzeDescription(form.job_description.trim());
  }

  async function handleLoadDemoJob() {
    setForm(demoFormState);
    setSubmitError(null);
    setSubmitSuccess(null);
    setAnalysisError(null);
    await analyzeDescription(demoFormState.job_description);
  }

  async function analyzeDescription(description: string) {
    if (!description) {
      setAnalysisError("Add a job description first.");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);
    setAnalysis(null);

    try {
      const response = await fetch(`${apiBaseUrl}/analyze-description`, {
        method: "POST",
        headers: createHeaders(true),
        body: JSON.stringify({ job_description: description }),
      });

      if (!response.ok) {
        const responseText = await response.text();
        throw new Error(
          responseText || `POST /analyze-description failed with ${response.status}`,
        );
      }

      setAnalysis((await response.json()) as DescriptionAnalysis);
    } catch (error) {
      setAnalysisError(
        error instanceof Error ? error.message : "Could not analyze this description.",
      );
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Local AI Job Tracker</p>
          <h1>Jobs workspace</h1>
        </div>
        <div className="header-actions">
          <span className="api-status">API: {apiBaseUrl}</span>
          <button type="button" className="secondary-button" onClick={fetchJobs}>
            Refresh
          </button>
        </div>
      </header>

      <section className="demo-strip">
        <div>
          <p className="eyebrow">Quick demo</p>
          <h2>Load a sample job, run the analyzer, and save it in one flow.</h2>
        </div>
        <button type="button" className="secondary-button" onClick={handleLoadDemoJob}>
          Load demo job
        </button>
      </section>

      <section className="workspace-grid">
        <form className="job-form" onSubmit={handleSubmit}>
          <div className="section-heading">
            <h2>Add job</h2>
            <p>Save a posting to PostgreSQL.</p>
          </div>

          <div className="field-row two-columns">
            <label>
              Company
              <input
                required
                value={form.company_name}
                onChange={(event) =>
                  updateField("company_name", event.target.value)
                }
                placeholder="OpenAI"
              />
            </label>

            <label>
              Job title
              <input
                required
                value={form.job_title}
                onChange={(event) => updateField("job_title", event.target.value)}
                placeholder="Data Analyst"
              />
            </label>
          </div>

          <label>
            Location
            <input
              value={form.location}
              onChange={(event) => updateField("location", event.target.value)}
              placeholder="London, Remote"
            />
          </label>

          <div className="field-row two-columns">
            <label>
              Salary min
              <input
                min="0"
                step="1"
                type="number"
                value={form.salary_min}
                onChange={(event) => updateField("salary_min", event.target.value)}
                placeholder="40000"
              />
            </label>

            <label>
              Salary max
              <input
                min="0"
                step="1"
                type="number"
                value={form.salary_max}
                onChange={(event) => updateField("salary_max", event.target.value)}
                placeholder="60000"
              />
            </label>
          </div>

          <label>
            Source URL
            <input
              type="url"
              value={form.source_url}
              onChange={(event) => updateField("source_url", event.target.value)}
              placeholder="https://example.com/job"
            />
          </label>

          <label>
            Application deadline
            <input
              type="date"
              value={form.application_deadline}
              onChange={(event) =>
                updateField("application_deadline", event.target.value)
              }
            />
          </label>

          <label>
            Job description
            <textarea
              required
              value={form.job_description}
              onChange={(event) =>
                updateField("job_description", event.target.value)
              }
              placeholder="Paste the full job posting here."
              rows={9}
            />
          </label>

          <div className="analysis-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={handleAnalyzeDescription}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? "Analyzing..." : "Analyze description"}
            </button>
            <p className="analysis-hint">
              Quick local analysis for portfolio demos and keyword extraction.
            </p>
          </div>

          {analysisError ? <p className="message error">{analysisError}</p> : null}

          {analysis ? (
            <section className="analysis-panel">
              <div className="section-heading">
                <h2>AI analysis</h2>
                <p>Summary, skill hints, and a simple fit score.</p>
              </div>
              <p className="analysis-summary">{analysis.summary}</p>
              <div className="analysis-meta">
                <span>Seniority: {analysis.seniority}</span>
                <span>Score: {analysis.score}/100</span>
              </div>
              {analysis.suggested_keywords.length > 0 ? (
                <div className="analysis-keywords">
                  {analysis.suggested_keywords.map((item) => (
                    <span key={item.keyword} className="keyword-pill">
                      {item.keyword}
                      <small>{Math.round(item.confidence * 100)}%</small>
                    </span>
                  ))}
                </div>
              ) : (
                <p className="state-text">No obvious keywords detected yet.</p>
              )}
            </section>
          ) : null}

          {submitError ? <p className="message error">{submitError}</p> : null}
          {submitSuccess ? (
            <p className="message success">{submitSuccess}</p>
          ) : null}

          <button type="submit" className="primary-button" disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : "Save job"}
          </button>
        </form>

        <section className="jobs-panel">
          <div className="section-heading table-heading">
            <div>
              <h2>Saved jobs</h2>
              <p>{jobs.length} total in the database.</p>
            </div>
          </div>

          {isLoadingJobs ? <p className="state-text">Loading saved jobs...</p> : null}
          {jobsError ? <p className="message error">{jobsError}</p> : null}

          {!isLoadingJobs && !jobsError && sortedJobs.length === 0 ? (
            <p className="state-text">No jobs saved yet.</p>
          ) : null}

          {!isLoadingJobs && !jobsError && sortedJobs.length > 0 ? (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Role</th>
                    <th>Location</th>
                    <th>Salary</th>
                    <th>Deadline</th>
                    <th>Status</th>
                    <th>Source</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedJobs.map((job) => (
                    <tr key={job.job_id}>
                      <td>{job.company_name}</td>
                      <td>{job.job_title}</td>
                      <td>{job.location || "-"}</td>
                      <td>{formatSalary(job.salary_min, job.salary_max)}</td>
                      <td>{formatDate(job.application_deadline)}</td>
                      <td>{job.application?.status ?? "Not Applied"}</td>
                      <td>
                        {job.source_url ? (
                          <a href={job.source_url} target="_blank" rel="noreferrer">
                            Open
                          </a>
                        ) : (
                          "-"
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </section>
      </section>
    </main>
  );
}

function emptyToNull(value: string) {
  const trimmedValue = value.trim();
  return trimmedValue ? trimmedValue : null;
}

function createHeaders(includeJsonContentType = false) {
  const headers: Record<string, string> = {};

  if (includeJsonContentType) {
    headers["Content-Type"] = "application/json";
  }

  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  return headers;
}

function numberOrNull(value: string) {
  if (!value.trim()) {
    return null;
  }

  return Number(value);
}

function formatSalary(min: number | null, max: number | null) {
  if (min === null && max === null) {
    return "-";
  }

  if (min !== null && max !== null) {
    return `${formatCurrency(min)} - ${formatCurrency(max)}`;
  }

  return formatCurrency(min ?? max ?? 0);
}

function formatCurrency(value: number) {
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
