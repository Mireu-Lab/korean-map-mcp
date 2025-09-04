package main

import (
	"korean-map-mcp/lib"
	"log/slog"
	"net/http"
	"os"
	"time"
)

// responseWriter는 http.ResponseWriter를 래핑하여 응답 상태 코드를 캡처합니다.
type responseWriter struct {
	http.ResponseWriter
	status int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.status = code
	rw.ResponseWriter.WriteHeader(code)
}

// loggingMiddleware는 들어오는 모든 HTTP 요청에 대한 정보를 로깅하는 미들웨어입니다.
func loggingMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		// ResponseWriter를 래핑하여 상태 코드를 캡처합니다.
		rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}

		next.ServeHTTP(rw, r)

		slog.Info("Handled request",
			"method", r.Method,
			"path", r.URL.Path,
			"status", rw.status,
			"duration", time.Since(start),
		)
	}
}
func main() {
	logger := lib.NewLogger()
	slog.SetDefault(logger)

	if os.Getenv("KAKAO_API_KEY") == "" {
		slog.Error("`KAKAO_API_KEY` 정의 되지 않았음.")
		os.Exit(1)
	}
	slog.Info("KAKAO_API_KEY", os.Getenv("KAKAO_API_KEY"))
	slog.Info("LOG_LEVEL", os.Getenv("LOG_LEVEL"))

	apiHandler := &lib.ApiHandler{Logger: logger}

	http.HandleFunc("/search/address", loggingMiddleware(apiHandler.AddressHandler))
	http.HandleFunc("/search/category", loggingMiddleware(apiHandler.CategoryHandler))
	http.HandleFunc("/geo/coord2address", loggingMiddleware(apiHandler.Coord2AddressHandler))
	http.HandleFunc("/geo/coord2regioncode", loggingMiddleware(apiHandler.Coord2RegionCodeHandler))
	http.HandleFunc("/search/keyword", loggingMiddleware(apiHandler.KeywordHandler))
	http.HandleFunc("/geo/transcoord", loggingMiddleware(apiHandler.TranscoordHandler))

	slog.Info("Starting MCP server on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		slog.Error("Failed to start server", "error", err)
		os.Exit(1)
	}
}
