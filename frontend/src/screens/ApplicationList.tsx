import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { listApplications, ApplicationResponse } from "../services/api";

export const ApplicationList: React.FC = () => {
  const [applications, setApplications] = useState<ApplicationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadApplications();
    // Poll every 30 seconds to get updates
    const interval = setInterval(() => {
      loadApplications(true);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadApplications = async (isBackground = false) => {
    if (!isBackground) {
      setLoading(true);
      setError(null);
    } else {
      setIsRefreshing(true);
    }

    try {
      const apps = await listApplications();
      setApplications(apps);
      setError(null);
    } catch (error) {
      console.error("Failed to load applications:", error);
      setError("Failed to load applications. Please try again.");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "SUBMITTED":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "INTERVIEW":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "OFFER":
        return "bg-green-100 text-green-800 border-green-200";
      case "REJECTED":
        return "bg-red-100 text-red-800 border-red-200";
      case "WITHDRAWN":
        return "bg-gray-100 text-gray-800 border-gray-200";
      case "REMINDER_SENT":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "ARCHIVED":
        return "bg-gray-100 text-gray-600 border-gray-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "SUBMITTED":
        return "📋";
      case "INTERVIEW":
        return "🤝";
      case "OFFER":
        return "🎉";
      case "REJECTED":
        return "❌";
      case "WITHDRAWN":
        return "↩️";
      case "REMINDER_SENT":
        return "⏰";
      case "ARCHIVED":
        return "📦";
      default:
        return "📋";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const LoadingSkeleton = () => (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
      <div className="animate-pulse">
        <div className="bg-gray-50 h-12"></div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="border-t border-gray-200 p-6">
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded-full w-20"></div>
              <div className="h-4 bg-gray-200 rounded w-16"></div>
              <div className="h-4 bg-gray-200 rounded w-20"></div>
              <div className="h-8 bg-gray-200 rounded w-20"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const EmptyState = () => (
    <div className="text-center py-16 bg-white rounded-lg shadow-md">
      <div className="text-6xl mb-4">🚀</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        Ready to start your job search?
      </h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        Track your applications with automated workflows, AI-generated cover
        letters, and smart deadline reminders.
      </p>
      <Link
        to="/applications/new"
        className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md"
      >
        <span className="text-lg mr-2">+</span>
        Add Your First Application
      </Link>
    </div>
  );

  const ErrorState = () => (
    <div className="text-center py-16 bg-white rounded-lg shadow-md border-2 border-red-100">
      <div className="text-6xl mb-4">⚠️</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        Oops! Something went wrong
      </h3>
      <p className="text-gray-600 mb-6">{error}</p>
      <button
        onClick={() => loadApplications()}
        className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
      >
        🔄 Try Again
      </button>
    </div>
  );

  const getApplicationStats = () => {
    const stats = applications.reduce((acc, app) => {
      acc[app.status] = (acc[app.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      total: applications.length,
      submitted: stats.SUBMITTED || 0,
      interview: stats.INTERVIEW || 0,
      offer: stats.OFFER || 0,
      rejected: stats.REJECTED || 0,
    };
  };

  const stats = getApplicationStats();

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Job Applications
            </h1>
            <p className="text-gray-600 mt-1">
              Track your job applications with automated workflows
            </p>
          </div>
        </div>
        <LoadingSkeleton />
      </div>
    );
  }

  if (error && applications.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Job Applications
            </h1>
            <p className="text-gray-600 mt-1">
              Track your job applications with automated workflows
            </p>
          </div>
        </div>
        <ErrorState />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div className="flex-1">
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold text-gray-900">
              Job Applications
            </h1>
            {isRefreshing && (
              <div className="flex items-center text-sm text-blue-600">
                <div className="animate-spin mr-2">🔄</div>
                Refreshing...
              </div>
            )}
          </div>
          <p className="text-gray-600 mt-1">
            Track your job applications with automated workflows
          </p>

          {/* Stats Summary */}
          {applications.length > 0 && (
            <div className="flex flex-wrap gap-4 mt-4">
              <div className="bg-blue-50 px-3 py-1 rounded-full text-sm">
                <span className="font-medium text-blue-700">
                  {applications.length}
                </span>
                <span className="text-blue-600 ml-1">Total</span>
              </div>
              {applications.filter((app) => app.status === "SUBMITTED").length >
                0 && (
                <div className="bg-yellow-50 px-3 py-1 rounded-full text-sm">
                  <span className="font-medium text-yellow-700">
                    {
                      applications.filter((app) => app.status === "SUBMITTED")
                        .length
                    }
                  </span>
                  <span className="text-yellow-600 ml-1">Pending</span>
                </div>
              )}
              {applications.filter((app) => app.status === "INTERVIEW").length >
                0 && (
                <div className="bg-blue-50 px-3 py-1 rounded-full text-sm">
                  <span className="font-medium text-blue-700">
                    {
                      applications.filter((app) => app.status === "INTERVIEW")
                        .length
                    }
                  </span>
                  <span className="text-blue-600 ml-1">Interview</span>
                </div>
              )}
              {applications.filter((app) => app.status === "OFFER").length >
                0 && (
                <div className="bg-green-50 px-3 py-1 rounded-full text-sm">
                  <span className="font-medium text-green-700">
                    {
                      applications.filter((app) => app.status === "OFFER")
                        .length
                    }
                  </span>
                  <span className="text-green-600 ml-1">Offers</span>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => loadApplications()}
            disabled={loading || isRefreshing}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors duration-200 disabled:opacity-50"
          >
            <span
              className={`mr-2 ${
                loading || isRefreshing ? "animate-spin" : ""
              }`}
            >
              🔄
            </span>
            Refresh
          </button>
          <Link
            to="/applications/new"
            className="flex items-center px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md"
          >
            <span className="text-lg mr-2">+</span>
            Add New Application
          </Link>
        </div>
      </div>

      {applications.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-lg shadow-md">
          <div className="text-6xl mb-4">🚀</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Ready to start your job search?
          </h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Track your applications with automated workflows, AI-generated cover
            letters, and smart deadline reminders.
          </p>
          <Link
            to="/applications/new"
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md"
          >
            <span className="text-lg mr-2">+</span>
            Add Your First Application
          </Link>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company & Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cover Letter
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Applied
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {applications.map((app) => (
                  <tr
                    key={app.id}
                    className="hover:bg-gray-50 transition-colors duration-150"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {app.company}
                        </div>
                        <div className="text-sm text-gray-500">{app.role}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(
                          app.status
                        )}`}
                      >
                        <span className="mr-1">
                          {getStatusIcon(app.status)}
                        </span>
                        {app.status.replace("_", " ")}
                      </span>
                      {app.reminder_sent && (
                        <div className="text-xs text-orange-600 mt-1 flex items-center">
                          <span className="mr-1">⏰</span> Reminder sent
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span
                          className={`text-sm flex items-center ${
                            app.cover_letter_available
                              ? "text-green-600"
                              : "text-gray-400"
                          }`}
                        >
                          <span className="mr-1">
                            {app.cover_letter_available ? "✅" : "⏳"}
                          </span>
                          {app.cover_letter_available
                            ? "Generated"
                            : "Generating..."}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {app.created_at ? formatDate(app.created_at) : "N/A"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <Link
                        to={`/applications/${app.id}`}
                        className="inline-flex items-center px-3 py-1 text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded-md transition-colors duration-200"
                      >
                        View Details →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
