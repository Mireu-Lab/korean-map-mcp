package lib

import "net/http"

// ### 4. 좌표계 변환
//
// 서로 다른 좌표계의 좌표를 변환하는 API입니다.
func (h *ApiHandler) TranscoordHandler(w http.ResponseWriter, r *http.Request) {
	h.ProxyKakaoRequest(w, r, "/v2/local/geo/transcoord.json")
}
