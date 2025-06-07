import axios from "axios";
import type {
  AnalysisResult,
  DiabetesRecord,
  InsightsResult,
} from "../types/analysis";

const API_BASE_URL = "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getAnalysisData = async (): Promise<AnalysisResult> => {
  const response = await axios.get(`${API_BASE_URL}/analyze`);
  return response.data;
};

export const getDiabetesRecords = async (
  limit: number = 100,
  offset: number = 0,
  minAge?: number,
  maxAge?: number,
  outcome?: boolean
): Promise<DiabetesRecord[]> => {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
    ...(minAge !== undefined && { min_age: minAge.toString() }),
    ...(maxAge !== undefined && { max_age: maxAge.toString() }),
    ...(outcome !== undefined && { outcome: outcome.toString() }),
  });

  const response = await axios.get(`${API_BASE_URL}/api/v1/data?${params}`);
  return response.data;
};

export const getInsights = async (): Promise<InsightsResult> => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/insights`);
  return response.data;
};

export const uploadDataset = async (formData: FormData) => {
  const response = await axios.post(
    `${API_BASE_URL}/api/v1/data/upload`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
};
