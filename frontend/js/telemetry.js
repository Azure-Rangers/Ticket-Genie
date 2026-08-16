/* =========================================================
   TICKETGENIE - FRONTEND DISTRIBUTED TELEMETRY & TRACING
   ========================================================= */

(function () {
  if (window.TicketGenieTelemetry) return;

  const Telemetry = {
    appInsights: null,
    initialized: false,

    async init() {
      if (this.initialized) return;

      try {
        // Fetch runtime config from backend /api/config
        const response = await fetch("/api/config").catch(() => null);
        let connectionString = "";

        if (response && response.ok) {
          const config = await response.json().catch(() => ({}));
          connectionString = config.appInsightsConnectionString || "";
        }

        if (!connectionString) {
          console.log("[Telemetry] No App Insights connection string found. Client telemetry disabled.");
          return;
        }

        // Load Application Insights JS SDK dynamically if not already loaded
        if (!window.Microsoft || !window.Microsoft.ApplicationInsights) {
          await this.loadSdkScript();
        }

        if (window.Microsoft && window.Microsoft.ApplicationInsights) {
          const snippet = new window.Microsoft.ApplicationInsights.ApplicationInsights({
            config: {
              connectionString: connectionString,
              enableCorsCorrelation: true,
              distributedTracingMode: 2, // W3C Distributed Tracing Mode
              enableAutoRouteTracking: true,
              enableUnhandledPromiseRejectionTracking: true,
              disableFetchTracking: false,
              disableAjaxTracking: false
            }
          });

          snippet.loadAppInsights();
          snippet.trackPageView({ name: document.title || window.location.pathname });

          this.appInsights = snippet;
          this.initialized = true;
          console.log("[Telemetry] Azure Application Insights client telemetry & W3C distributed tracing initialized.");
        }
      } catch (err) {
        console.warn("[Telemetry] Initialization failed:", err);
      }
    },

    loadSdkScript() {
      return new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = "https://js.monitor.azure.com/scripts/b/ai.2.min.js";
        script.async = true;
        script.onload = () => resolve();
        script.onerror = (err) => reject(err);
        document.head.appendChild(script);
      });
    },

    trackEvent(name, properties = {}) {
      if (this.appInsights) {
        this.appInsights.trackEvent({ name }, properties);
      }
    },

    trackPageView(name) {
      if (this.appInsights) {
        this.appInsights.trackPageView({ name: name || document.title });
      }
    },

    trackException(exception, severityLevel) {
      if (this.appInsights) {
        this.appInsights.trackException({ exception, severityLevel });
      }
    }
  };

  window.TicketGenieTelemetry = Telemetry;

  // Auto-initialize when page loads
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => Telemetry.init());
  } else {
    Telemetry.init();
  }
})();
