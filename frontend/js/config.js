/**
 * API URL for deployment.
 * After deploying the backend on Railway, replace YOUR-BACKEND with your service URL.
 * Example: https://apriori-counter-api-production.up.railway.app
 */
(function () {
  const isLocal =
    location.hostname === "localhost" ||
    location.hostname === "127.0.0.1" ||
    location.hostname === "";

  window.API_BASE =
    window.API_BASE ||
    (isLocal ? "http://127.0.0.1:8000" : "https://YOUR-BACKEND.up.railway.app");
})();
