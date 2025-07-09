const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface ApplicationForm {
  company: string;
  role: string;
  jobDescription: string;
  resume: string;
  userEmail: string;
  deadlineWeeks: number;
}

export interface ApplicationResponse {
  id: string;
  workflow_id: string;
  status: string;
  company: string;
  role: string;
  cover_letter_available: boolean;
  reminder_sent: boolean;
  created_at: string;
}

export interface CoverLetterResponse {
  cover_letter: string;
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async createApplication(data: ApplicationForm): Promise<ApplicationResponse> {
    // Convert camelCase to snake_case for API
    const apiData = {
      company: data.company,
      role: data.role,
      job_description: data.jobDescription,
      resume: data.resume,
      user_email: data.userEmail,
      deadline_weeks: data.deadlineWeeks
    };
    
    return this.request<ApplicationResponse>('/api/applications/', {
      method: 'POST',
      body: JSON.stringify(apiData),
    });
  }

  async listApplications(): Promise<ApplicationResponse[]> {
    return this.request<ApplicationResponse[]>('/api/applications/');
  }

  async getApplication(id: string): Promise<ApplicationResponse> {
    return this.request<ApplicationResponse>(`/api/applications/${id}`);
  }

  async updateStatus(id: string, status: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/applications/${id}/status`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    });
  }

  async getCoverLetter(id: string): Promise<CoverLetterResponse> {
    return this.request<CoverLetterResponse>(`/api/applications/${id}/cover-letter`);
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/api/health/');
  }
}

export const apiService = new ApiService();

// Export individual functions for convenience with proper binding
export const createApplication = (data: ApplicationForm) => apiService.createApplication(data);
export const listApplications = () => apiService.listApplications();
export const getApplication = (id: string) => apiService.getApplication(id);
export const updateStatus = (id: string, status: string) => apiService.updateStatus(id, status);
export const getCoverLetter = (id: string) => apiService.getCoverLetter(id);
export const healthCheck = () => apiService.healthCheck();