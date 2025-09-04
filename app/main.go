package main

import (
	"korean-map-mcp/lib"
	"log/slog"
	"net/http"
	"os"
)

// loggingMiddleware는 들어오는 모든 HTTP 요청에 대한 정보를 로깅하는 미들웨어입니다.
func loggingMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		slog.Info("Incoming request",
			"method", r.Method,
			"path", r.URL.Path,
			"remote_addr", r.RemoteAddr,
		)
		next.ServeHTTP(w, r)
	}
}
func main() {
	logger := lib.NewLogger()
	slog.SetDefault(logger)

	if os.Getenv("KAKAO_API_KEY") == "" {
		slog.Error("`KAKAO_API_KEY` 정의 되지 않았음.")
		os.Exit(1)
	}

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
