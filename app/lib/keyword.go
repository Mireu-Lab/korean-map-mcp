package lib

import "net/http"

// ### 5. 키워드로 장소 검색
//
// 특정 키워드로 장소를 검색하는 API입니다.
// 중심 좌표와 반경을 지정하여 검색할 수도 있습니다.
func (h *ApiHandler) KeywordHandler(w http.ResponseWriter, r *http.Request) {
	h.ProxyKakaoRequest(w, r, "/v2/local/search/keyword.json")
}
