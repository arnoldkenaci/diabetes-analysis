export interface AnalysisData {
  id: string;
  age_risk: string;
  bmi_risk: string;
  high_glucose: boolean;
  obesity: boolean;
}

export interface AnalysisSummary {
  summary: string;
  recommendations: string[];
}

export interface AnalysisResult {
  total_records: number;
  positive_cases: number;
  positive_rate: number;
  average_glucose: number;
  average_bmi: number;
  average_age: number;
  recommendations?: string[];
  risk_assessment?: string;
  preventive_measures?: string[];
}

export interface DiabetesRecord {
  id: number;
  age: number;
  bmi: number;
  glucose: number;
  outcome: boolean;
}

export interface DiabetesRecordList {
  total: number;
  offset: number;
  limit: number;
  data: DiabetesRecord[];
}

export interface AgeGroupInsight {
  age_range: string;
  count: number;
  diabetes_rate: number;
}

export interface BMICategoryInsight {
  category: string;
  count: number;
  diabetes_rate: number;
}

export interface InsightsResult {
  age_groups: AgeGroupInsight[];
  bmi_categories: BMICategoryInsight[];
}
