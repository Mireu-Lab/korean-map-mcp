package lib

import "net/http"

// ### 6. 카테고리로 장소 검색
//
// 미리 정의된 카테고리 코드를 이용해 장소를 검색하는 API입니다.
func (h *ApiHandler) CategoryHandler(w http.ResponseWriter, r *http.Request) {
	h.ProxyKakaoRequest(w, r, "/v2/local/search/category.json")
}
