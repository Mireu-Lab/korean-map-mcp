package main

import (
	"korean-map-mcp/lib"
	"log/slog"
	"net/http"
	"os"
)

func main() {
	logger := lib.NewLogger()
	slog.SetDefault(logger)

	if os.Getenv("KAKAO_API_KEY") == "" {
		slog.Error("`KAKAO_API_KEY` 정의 되지 않았음.")
		os.Exit(1)
	}

	apiHandler := &lib.ApiHandler{Logger: logger}

	http.HandleFunc("/search/address", apiHandler.AddressHandler)
	http.HandleFunc("/search/category", apiHandler.CategoryHandler)
	http.HandleFunc("/geo/coord2address", apiHandler.Coord2AddressHandler)
	http.HandleFunc("/geo/coord2regioncode", apiHandler.Coord2RegionCodeHandler)
	http.HandleFunc("/search/keyword", apiHandler.KeywordHandler)
	http.HandleFunc("/geo/transcoord", apiHandler.TranscoordHandler)

	slog.Info("Starting MCP server on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		slog.Error("Failed to start server", "error", err)
		os.Exit(1)
	}
}
