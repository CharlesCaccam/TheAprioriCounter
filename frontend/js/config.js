/**
 * Production API URL — update after Railway generates your backend domain.
 * Find it: Railway → TheAprioriCounter service → Settings → Networking → Public domain
 */
(function () {
  const isLocal =
    location.hostname === "localhost" ||
    location.hostname === "127.0.0.1";

  window.API_BASE =
    window.API_BASE ||
    (isLocal
      ? "http://127.0.0.1:8000"
      : "https://theaprioricounter-production.up.railway.app");
})();
