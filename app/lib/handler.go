package lib

import (
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
)

const kakaoAPIURL = "https://dapi.kakao.com"

type ApiHandler struct {
	Logger *slog.Logger
}

func (h *ApiHandler) ProxyKakaoRequestStream(w http.ResponseWriter, r *http.Request, path string) {
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	var err error

	targetURL := kakaoAPIURL + path + "?" + r.URL.RawQuery
	slog.Info("Proxying SSE request", "url", targetURL)

	client := &http.Client{}
	req, err := http.NewRequest("GET", targetURL, nil)
	req.Header.Set("Authorization", "KakaoAK "+os.Getenv("KAKAO_API_KEY"))
	if err != nil {
		slog.Error("Failed to create request", "error", err)
		return
	}

	resp, err := client.Do(req)
	if err != nil {
		slog.Error("Failed to call Kakao API", "error", err)
		return
	}
	defer resp.Body.Close()
	slog.Debug("Kakao API response status", "status", resp.Status)
	slog.Debug("Kakao API response headers", "headers", resp.Header)

	body, _ := io.ReadAll(resp.Body)
	slog.Debug("Kakao API response body", "body", string(body))

	fmt.Fprintf(w, "data: %s\n\n", body)
	flusher, _ := w.(http.Flusher)
	flusher.Flush()
}
