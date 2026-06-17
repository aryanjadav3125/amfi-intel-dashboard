/**
 * AMFI Dashboard API Client library
 * 
 * This module exports TypeScript interfaces matching the backend data structures
 * and asynchronous fetch functions that interface directly with the FastAPI backend.
 * All API calls are routed through the `fetchJson` utility for standardized error handling.
 */

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export interface FundSummary {
  scheme_id: number;
  scheme_name: string;
  category: string;
  scheme_type: string;
  latest_nav: number;
  latest_date: string | null;
  cagr_1y: number | null;
  
  asset_class: string | null;
  benchmark_name: string | null;
  scheme_riskometer: string | null;
  benchmark_riskometer: string | null;
  regular_nav: number | null;
  direct_nav: number | null;
  regular_cagr_5y: number | null;
  direct_cagr_5y: number | null;
  benchmark_cagr_5y: number | null;
  regular_info_ratio: number | null;
  direct_info_ratio: number | null;
  daily_aum: number | null;
}

export interface FundListResponse {
  funds: FundSummary[];
  total: number;
}

export interface AssetAllocation {
  asset_class: string;
  percentage: number;
}

export interface FundMetrics {
  cagr_1y: number | null;
  cagr_3y: number | null;
  volatility: number | null;
  sharpe_ratio: number | null;
  sortino_ratio: number | null;
  max_drawdown: number | null;
}

export interface FundDetails {
  scheme_id: number;
  scheme_name: string;
  category: string;
  scheme_type: string;
  isin_growth: string | null;
  isin_div_payout: string | null;
  latest_nav: number;
  latest_date: string | null;
  allocations: AssetAllocation[];
  metrics: FundMetrics;
  
  asset_class: string | null;
  benchmark_name: string | null;
  scheme_riskometer: string | null;
  benchmark_riskometer: string | null;
  regular_nav: number | null;
  direct_nav: number | null;
  regular_cagr_5y: number | null;
  direct_cagr_5y: number | null;
  benchmark_cagr_5y: number | null;
  regular_info_ratio: number | null;
  direct_info_ratio: number | null;
  daily_aum: number | null;
}

export interface NavHistoryPoint {
  date: string;
  nav: number;
  regular_nav?: number | null;
}

export interface SipPoint {
  date: string;
  invested: number;
  value: number;
}

export interface SipSimulationResponse {
  total_investment: number;
  final_value: number;
  profit: number;
  absolute_returns: number;
  annualized_returns: number | null;
  chart: SipPoint[];
}

export interface CompareMatrixRow {
  scheme_id: number;
  scheme_name: string;
  category: string;
  latest_nav: number;
  cagr_1y: number | null;
  cagr_3y: number | null;
  volatility: number | null;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
}

export interface CompareResponse {
  matrix: CompareMatrixRow[];
  chart: Array<Record<string, any>>;
}

export interface PipelineStatus {
  run_id: number | null;
  run_type: string | null;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  records_inserted: number;
  records_skipped: number;
  errors_count: number;
}

/**
 * Generic fetch wrapper for querying the FastAPI backend.
 * Checks for non-ok responses and throws appropriately.
 */
export async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error (${response.status}): ${text || response.statusText}`);
  }

  return response.json() as Promise<T>;
}

/**
 * Fetch a paginated and optionally filtered list of funds.
 * Used for the Screener and the Top Performers table.
 */
export async function getFunds(params: {
  category?: string;
  amc_id?: number;
  q?: string;
  scheme_type?: string;
  asset_class?: string;
  limit?: number;
  offset?: number;
}): Promise<FundListResponse> {
  const query = new URLSearchParams();
  if (params.category) query.append("category", params.category);
  if (params.amc_id) query.append("amc_id", String(params.amc_id));
  if (params.q) query.append("q", params.q);
  if (params.scheme_type) query.append("scheme_type", params.scheme_type);
  if (params.asset_class) query.append("asset_class", params.asset_class);
  if (params.limit) query.append("limit", String(params.limit));
  if (params.offset) query.append("offset", String(params.offset));

  return fetchJson<FundListResponse>(`/funds?${query.toString()}`);
}

/**
 * Retrieves detailed metrics, allocations, and core metadata for a single fund.
 */
export async function getFundDetails(schemeId: number): Promise<FundDetails> {
  return fetchJson<FundDetails>(`/funds/${schemeId}`);
}

/**
 * Retrieves the historical NAV sequence for a specific fund to render performance charts.
 */
export async function getFundNavHistory(
  schemeId: number,
  startDate?: string,
  endDate?: string
): Promise<NavHistoryPoint[]> {
  const query = new URLSearchParams();
  if (startDate) query.append("start_date", startDate);
  if (endDate) query.append("end_date", endDate);
  return fetchJson<NavHistoryPoint[]>(`/funds/${schemeId}/nav?${query.toString()}`);
}

export async function simulateSip(
  schemeId: number,
  monthlyInvestment: number,
  years: number
): Promise<SipSimulationResponse> {
  return fetchJson<SipSimulationResponse>(
    `/funds/${schemeId}/sim-sip?monthly_investment=${monthlyInvestment}&years=${years}`
  );
}

export async function getCategories(): Promise<string[]> {
  return fetchJson<string[]>("/categories");
}

export async function getCategoriesSummary(): Promise<Array<{ category: string; fund_count: number }>> {
  return fetchJson<Array<{ category: string; fund_count: number }>>("/categories/summary");
}

export async function getCategoryLeaders(category: string, limit: number = 10): Promise<FundSummary[]> {
  return fetchJson<FundSummary[]>(`/categories/${encodeURIComponent(category)}/leaders?limit=${limit}`);
}

export async function compareFunds(schemeIds: number[], startDate?: string, endDate?: string): Promise<CompareResponse> {
  const query = new URLSearchParams();
  query.append("ids", schemeIds.join(","));
  if (startDate) query.append("start_date", startDate);
  if (endDate) query.append("end_date", endDate);
  return fetchJson<CompareResponse>(`/compare?${query.toString()}`);
}

export async function getPipelineStatus(): Promise<PipelineStatus> {
  return fetchJson<PipelineStatus>("/pipeline/status");
}

export interface AmcResponse {
  fund_house_id: number;
  name: string;
  code: string | null;
}

export async function getAmcs(): Promise<AmcResponse[]> {
  return fetchJson<AmcResponse[]>("/funds/amcs");
}

export interface AumAmcMetric {
  fund_house_id: number;
  amc_name: string;
  average_aum: number;
  aaum: number;
  direct_aum: number | null;
  regular_aum: number | null;
  t15_aum: number | null;
  b15_aum: number | null;
  folio_count: number | null;
}

export interface AumSummaryResponse {
  period: string;
  total_avg_aum: number;
  total_aaum: number;
  total_folios: number;
  direct_percentage: number;
  regular_percentage: number;
  amcs: AumAmcMetric[];
}

export async function getAumSummary(period?: string): Promise<AumSummaryResponse> {
  const query = period ? `?period=${encodeURIComponent(period)}` : "";
  return fetchJson<AumSummaryResponse>(`/aum/summary${query}`);
}

export interface CategoryAumResponse {
  category: string;
  period: string;
  aum_value: number;
  folio_count: number | null;
  percentage_of_total: number | null;
}

export async function getCategoryAum(period?: string): Promise<CategoryAumResponse[]> {
  const query = period ? `?period=${encodeURIComponent(period)}` : "";
  return fetchJson<CategoryAumResponse[]>(`/aum/categories${query}`);
}

export interface DashboardOverview {
  total_funds: number;
  total_categories: number;
  total_amcs: number;
  latest_nav_update: string;
}

/**
 * Retrieves the high-level dashboard metrics used for the overview structural cards.
 * 
 * @returns DashboardOverview object containing counts and latest sync timestamp
 */
export async function getDashboardOverview(): Promise<DashboardOverview> {
  return fetchJson<DashboardOverview>("/dashboard/overview");
}

export interface PortfolioOverlapResponse {
  common_holdings: string[];
  overlap_percentage: number;
  sector_similarity: Record<string, number>;
  diversification_score: number;
  concentration_risk: string;
}

export async function calculatePortfolioOverlap(schemeIds: number[]): Promise<PortfolioOverlapResponse> {
  return fetchJson<PortfolioOverlapResponse>("/portfolios/overlap", {
    method: "POST",
    body: JSON.stringify(schemeIds),
  });
}
