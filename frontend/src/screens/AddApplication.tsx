import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createApplication, ApplicationForm } from "../services/api";

export const AddApplication: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<ApplicationForm>({
    company: "",
    role: "",
    jobDescription: "",
    resume: "",
    userEmail: "",
    deadlineWeeks: 4,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await createApplication(form);
      navigate(`/applications/${response.id}`, {
        state: {
          message:
            "Application created successfully! Cover letter is being generated...",
        },
      });
    } catch (error) {
      console.error("Failed to create application:", error);
      setError(
        "Failed to create application. Please check your inputs and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    field: keyof ApplicationForm,
    value: string | number
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Add New Application
        </h1>
        <p className="text-gray-600">
          Start tracking a new job application with automated workflows
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-6 bg-white shadow-md rounded-lg p-6"
      >
        {error && (
          <div
            className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4"
            role="alert"
          >
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company *
          </label>
          <input
            type="text"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={form.company}
            onChange={(e) => handleChange("company", e.target.value)}
            placeholder="e.g., Google, Microsoft, Startup Inc."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Role *
          </label>
          <input
            type="text"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={form.role}
            onChange={(e) => handleChange("role", e.target.value)}
            placeholder="e.g., Software Engineer, Product Manager"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Description *
          </label>
          <textarea
            required
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={form.jobDescription}
            onChange={(e) => handleChange("jobDescription", e.target.value)}
            placeholder="Paste the job description here..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Resume *
          </label>
          <textarea
            required
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Paste your resume content here..."
            value={form.resume}
            onChange={(e) => handleChange("resume", e.target.value)}
          />
          <p className="text-sm text-gray-500 mt-1">
            This will be used to generate a personalized cover letter
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email Address *
          </label>
          <input
            type="email"
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={form.userEmail}
            onChange={(e) => handleChange("userEmail", e.target.value)}
            placeholder="your.email@example.com"
          />
          <p className="text-sm text-gray-500 mt-1">
            For deadline reminders and notifications
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Deadline (weeks from now)
          </label>
          <input
            type="number"
            min="1"
            max="12"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={form.deadlineWeeks}
            onChange={(e) =>
              handleChange("deadlineWeeks", parseInt(e.target.value))
            }
          />
          <p className="text-sm text-gray-500 mt-1">
            You'll get a reminder if there's no update by this deadline
          </p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors duration-200"
        >
          {loading ? (
            <>
              <div className="animate-spin mr-2">⏳</div>
              Creating Application...
            </>
          ) : (
            <>
              <span className="mr-2">🚀</span>
              Start Application Workflow
            </>
          )}
        </button>
      </form>
    </div>
  );
};
