export interface DiabetesRecord {
  id: number;
  glucose: number;
  bmi: number;
  age: number;
  diabetes: boolean;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  anomalies: {
    age: Array<{
      record_id: number;
      value: number;
      deviation: number;
    }>;
    bmi: Array<{
      record_id: number;
      value: number;
      deviation: number;
    }>;
    glucose: Array<{
      record_id: number;
      value: number;
      deviation: number;
    }>;
  };
  average_age: number;
  average_bmi: number;
  average_glucose: number;
}

export interface InsightsResult {
  age_groups: Array<{
    age_range: string;
    count: number;
    diabetes_rate: number;
  }>;
  bmi_risk: string;
}

export interface UploadResponse {
  message: string;
  records_uploaded: number;
}
