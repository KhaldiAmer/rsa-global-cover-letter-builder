import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  getApplication,
  updateStatus,
  getCoverLetter,
  ApplicationResponse,
} from "../services/api";

const STATUS_OPTIONS = [
  {
    value: "INTERVIEW",
    label: "Interview Scheduled",
    icon: "🤝",
    color: "bg-blue-600 hover:bg-blue-700",
  },
  {
    value: "OFFER",
    label: "Offer Received",
    icon: "🎉",
    color: "bg-green-600 hover:bg-green-700",
  },
  {
    value: "REJECTED",
    label: "Rejected",
    icon: "❌",
    color: "bg-red-600 hover:bg-red-700",
  },
  {
    value: "WITHDRAWN",
    label: "Withdrawn",
    icon: "↩️",
    color: "bg-gray-600 hover:bg-gray-700",
  },
];

export const ApplicationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [application, setApplication] = useState<ApplicationResponse | null>(
    null
  );
  const [coverLetter, setCoverLetter] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);

  useEffect(() => {
    if (id) {
      loadApplication();
      const interval = setInterval(loadApplication, 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }
  }, [id]);

  const loadApplication = async () => {
    if (!id) return;

    try {
      const app = await getApplication(id);
      setApplication(app);

      if (app.cover_letter_available && !coverLetter) {
        try {
          const letter = await getCoverLetter(id);
          setCoverLetter(letter.cover_letter);
        } catch (error) {
          console.error("Failed to load cover letter:", error);
        }
      }
    } catch (error) {
      console.error("Failed to load application:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus: string) => {
    if (!id) return;

    setUpdating(true);
    try {
      await updateStatus(id, newStatus);
      await loadApplication();
      setSuccessMessage(`Status updated to ${newStatus}!`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (error) {
      console.error("Failed to update status:", error);
      setError("Failed to update status. Please try again.");
      setTimeout(() => setError(null), 3000);
    } finally {
      setUpdating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "SUBMITTED":
        return "bg-yellow-100 text-yellow-800";
      case "INTERVIEW":
        return "bg-blue-100 text-blue-800";
      case "OFFER":
        return "bg-green-100 text-green-800";
      case "REJECTED":
        return "bg-red-100 text-red-800";
      case "WITHDRAWN":
        return "bg-gray-100 text-gray-800";
      case "REMINDER_SENT":
        return "bg-orange-100 text-orange-800";
      case "ARCHIVED":
        return "bg-gray-100 text-gray-600";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading application...</div>
      </div>
    );
  }

  if (!application) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-red-600 mb-4">Application not found</div>
          <Link to="/" className="text-blue-600 hover:text-blue-800">
            ← Back to Applications
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Success/Error Messages */}
      {successMessage && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-green-500">✅</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">
                {successMessage}
              </p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-red-500">❌</span>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="mb-6">
        <Link
          to="/"
          className="text-blue-600 hover:text-blue-800 mb-4 inline-block"
        >
          ← Back to Applications
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">
          {application.company} - {application.role}
        </h1>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Application Status</h2>

        <div className="mb-4">
          <span className="text-sm text-gray-600">Current Status:</span>
          <span
            className={`ml-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
              application.status
            )}`}
          >
            {application.status}
          </span>
        </div>

        {application.reminder_sent && (
          <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded">
            <p className="text-orange-800">
              ⏰ Reminder sent - deadline approaching! Consider following up.
            </p>
          </div>
        )}

        <div className="mb-4">
          <span className="text-sm text-gray-600">Cover Letter:</span>
          <span
            className={`ml-2 text-sm ${
              application.cover_letter_available
                ? "text-green-600"
                : "text-gray-500"
            }`}
          >
            {application.cover_letter_available
              ? "✓ Generated"
              : "⏳ Generating..."}
          </span>
        </div>

        {application.status === "SUBMITTED" && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">Update Status:</p>
            <div className="flex flex-wrap gap-2">
              {STATUS_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleStatusUpdate(option.value)}
                  disabled={updating}
                  className={`px-4 py-2 rounded-full text-white text-sm font-medium flex items-center justify-center ${
                    option.color
                  } ${updating ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  {option.icon} {updating ? "Updating..." : option.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {coverLetter && (
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Generated Cover Letter</h2>
          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
              {coverLetter}
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => {
                navigator.clipboard.writeText(coverLetter);
                setCopySuccess(true);
                setTimeout(() => setCopySuccess(false), 2000);
              }}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              {copySuccess ? "Copied!" : "Copy to Clipboard"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
