package lib

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
)

// ProxyKakaoRequest는 들어오는 요청을 카카오 API로 전달하는 범용 프록시 함수입니다.
func (h *ApiHandler) ProxyKakaoRequest(w http.ResponseWriter, r *http.Request, apiPath string) {
	// 1. 카카오 API URL 구성
	kakaoBaseURL := "https://dapi.kakao.com"
	targetURL, err := url.Parse(kakaoBaseURL + apiPath)
	if err != nil {
		h.Logger.Error("잘못된 URL 생성", "error", err)
		http.Error(w, "내부 서버 오류", http.StatusInternalServerError)
		return
	}
	targetURL.RawQuery = r.URL.RawQuery

	// 2. 카카오 API로 보낼 새 요청 생성
	proxyReq, err := http.NewRequest(r.Method, targetURL.String(), r.Body)
	if err != nil {
		h.Logger.Error("프록시 요청 생성 실패", "error", err)
		http.Error(w, "내부 서버 오류", http.StatusInternalServerError)
		return
	}

	KAKAO_API_KEY := os.Getenv("KAKAO_API_KEY")
	KAKAO_API_KEY = fmt.Sprintf("KakaoAK %s", KAKAO_API_KEY)

	// 3. 클라이언트의 Authorization 헤더 복사
	proxyReq.Header.Set("Authorization", KAKAO_API_KEY)

	// 4. 요청 실행
	client := &http.Client{}
	resp, err := client.Do(proxyReq)
	if err != nil {
		h.Logger.Error("카카오 API 요청 실패", "error", err)
		http.Error(w, "게이트웨이 오류", http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	// 5. 카카오 API의 응답을 클라이언트에게 다시 복사
	// 헤더 복사
	for key, values := range resp.Header {
		for _, value := range values {
			w.Header().Add(key, value)
		}
	}

	// 상태 코드 설정
	w.WriteHeader(resp.StatusCode)

	// 바디 복사
	if _, err := io.Copy(w, resp.Body); err != nil {
		h.Logger.Error("응답 바디 복사 실패", "error", err)
	}
}
