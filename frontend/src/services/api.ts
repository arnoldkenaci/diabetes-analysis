import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

// Initialize axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types for API requests and responses
export interface UserData {
  name: string;
  surname: string;
  email: string;
}

export interface UserResponse {
  id: number;
  name: string;
  surname: string;
  email: string;
  created_at: string;
  updated_at: string | null;
}

export interface DiabetesRecordData {
  user_id: number;
  pregnancies: number | null;
  glucose: number;
  blood_pressure: number;
  skin_thickness: number;
  insulin: number;
  bmi: number;
  diabetes_pedigree: number;
  age: number;
}

export interface DiabetesRecordResponse {
  id: number;
  user_id: number;
  pregnancies: number | null;
  glucose: number;
  blood_pressure: number;
  skin_thickness: number;
  insulin: number;
  bmi: number;
  diabetes_pedigree: number;
  age: number;
  outcome: boolean;
  source: string;
  created_at: string;
  updated_at: string | null;
}

export interface HealthAssessmentResponse {
  id: number;
  user_id: number;
  diabetes_record_id: number;
  risk_score: number;
  risk_level: string;
  recommendations: {
    risk_assessment: string;
    recommendations: string[];
    preventive_measures: string[];
  };
  created_at: string;
  updated_at: string | null;
}

/**
 * Fetches a specific health assessment by ID
 * @param assessmentId The ID of the health assessment to fetch
 * @returns Health assessment data
 * @throws Error if request fails
 */
export const getHealthAssessment = async (
  assessmentId: number
): Promise<HealthAssessmentResponse> => {
  try {
    const response = await api.get<HealthAssessmentResponse>(
      `/api/v1/health/${assessmentId}`
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail || "Failed to fetch health assessment"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};

/**
 * Creates a new user in the system
 * @param userData User information
 * @returns User data
 * @throws Error if user creation fails
 */
export const createUser = async (userData: UserData): Promise<UserResponse> => {
  const response = await api.post<UserResponse>("/api/v1/users/", userData);
  return response.data;
};

/**
 * Creates a new diabetes record for a user
 * @param recordData Diabetes record information
 * @returns Created diabetes record
 * @throws Error if record creation fails
 */
export const createDiabetesRecord = async (
  recordData: DiabetesRecordData
): Promise<DiabetesRecordResponse> => {
  try {
    const response = await api.post<DiabetesRecordResponse>(
      "/api/v1/diabetes/",
      recordData
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error("User not found");
      }
      throw new Error(
        error.response?.data?.detail || "Failed to create diabetes record"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};

/**
 * Creates a new user and their initial diabetes record and health assessment
 * @param userData User information
 * @param recordData Diabetes record information
 * @returns Created user, diabetes record, and health assessment
 * @throws Error if any operation fails
 */
export const createInitialUserWithRecord = async (
  userData: UserData,
  recordData: Omit<DiabetesRecordData, "user_id">
): Promise<{
  user: UserResponse;
  record: DiabetesRecordResponse;
}> => {
  try {
    let user: UserResponse;
    try {
      // Try to create user first
      user = await createUser(userData);
    } catch (error) {
      // If user already exists (409), extract user data from error response
      if (axios.isAxiosError(error) && error.response?.status === 409) {
        user = error.response.data as UserResponse;
      } else {
        throw new Error("Failed to create user!");
      }
    }

    // Create diabetes record with the user's ID
    const record = await createDiabetesRecord({
      ...recordData,
      user_id: user.id,
    });

    return {
      user,
      record,
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail ||
          "Failed to create user, record, or assessment"
      );
    }
    throw new Error("An unexpected error occurred");
  }
};
